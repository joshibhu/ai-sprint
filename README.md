# ai-sprint

A 30-day, build-every-day sprint to learn AI engineering — integrating language
models into real products, not training them.

This README is my learning log. Each day records what I built, the concepts
worth keeping, and what surprised me. The code is in the repo; this is the part
I would not be able to reconstruct from the code a year from now.

**Stack so far:** Python 3.12 · uv · pydantic · FastAPI · OpenAI SDK

```bash
uv run python -m sprint "a question"      # one-shot
uv run python -m sprint                   # chat
uv run python scripts/score.py            # extraction scorecard
uv run uvicorn sprint.api:app --reload    # the service, docs at /docs
```

---

## Day 1 — A CLI that calls a model

**Built:** a command-line tool that sends one prompt and prints the answer.

**Core concepts**

- `uv` owns the virtual environment. `uv add` to install, `uv run` to execute.
  Never `pip install` — mixing the two is how Python environments rot.
- Config is a typed object, not scattered `os.environ` reads. `pydantic-settings`
  binds environment variables to a class and **fails at startup** if the API key
  is missing, rather than at the first request. (Java: `@ConfigurationProperties`.)
- Secrets live in `.env`, which is gitignored. `.env.example` is committed with
  blank values so anyone cloning knows what to set.
- **One file imports the vendor SDK.** Everything else talks to my own function.
  Swapping providers later is then a one-file change, and I can say so to a client.
- Type hints are not enforced at runtime — they are for the IDE and linters only.
  Plain Python would ignore them; pydantic is what actually validates.

**What bit me**

`.env` is loaded into *my settings object*, not into the process environment. So
the SDK's zero-argument constructor does not see the key — it has to be passed
in explicitly. The error looks like a missing key while the file plainly has one.

---

## Day 2 — Streaming chat, and what it costs

**Built:** a chat loop that streams the reply word by word and prints the token
cost of every turn.

**Core concepts**

- **The API has no memory.** Nothing is stored server-side. Each turn I resend
  the entire conversation. The list of messages in my process *is* the memory —
  lose it and the conversation is gone.
- Because of that, **cost grows with the square of the conversation length.**
  I am not paying for 20 questions; I am paying for question 1 twenty times,
  question 2 nineteen times, and so on. Clients never anticipate this.
- Three roles: `system` (standing instruction, resent every turn and billed
  every turn), `user`, `assistant` (the model's earlier replies, played back).
- **Streaming is a UX feature, not a speed feature.** The answer takes the same
  time; it just starts appearing immediately instead of after eight seconds.
- Output tokens cost several times more than input tokens. "Be concise" in a
  system prompt is a cost control, not only a style choice.

**What bit me**

*Reasoning tokens.* My model thinks before answering, and that thinking is
**billed as output but never shown**. One turn: 2,300 output tokens billed,
124 visible. **94% of the output charge bought tokens I cannot read.**

They are also *discarded*, not kept — they never enter the next turn's input,
which is why input grows more slowly than the output numbers suggest.

This is the only line of the bill I cannot verify. I can count my own prompt
tokens; I cannot count reasoning I never see. The answer is not to audit it but
to **bound it** — a hard ceiling on total output tokens per call — and to log
the ratio so drift would be visible.

Second thing: the model was *confidently wrong* about domain facts, twice, in
two different ways across two runs. 2,176 tokens of reasoning cannot invent
knowledge that is not in the model. Reasoning helps with deduction, not recall.
That is the argument for retrieval, discovered first-hand.

**Measured:** ~₹84 per 1,000 questions on this model — with the caveat above.

---

## Day 3 — Structured data out of documents

**Built:** PDF invoice → validated typed object. Ten synthetic invoices, each
planting one extraction trap, plus a scorecard that grades against known answers.

**Core concepts**

- Asking for JSON in the prompt gets JSON *most* of the time. **Structured
  outputs constrain generation** so the shape is guaranteed — no markdown
  fences, no preamble, no renamed fields. A different mechanism, not a better
  prompt. (Java: handing Jackson a target type — except the upstream is *forced*
  to comply rather than merely expected to.)
- **The field descriptions in the schema are sent to the model.** They are
  prompt text, not comments. Vague descriptions produce vague extraction.
- **Valid shape ≠ correct answer.** The extractor returned a perfectly typed,
  fully validated invoice where the vendor was actually the customer. Nothing in
  the code caught it — not the API, not the validation. Only the ground-truth
  file caught it.
- Therefore: no silent defaults. If a field cannot be read, say so loudly. A
  crash is noticed today; a wrong number in a database is noticed at audit.
- Keep the model's job narrow: *"what does the document say?"* My code decides
  *"what does that mean?"* Ask it for the date as printed, parse it in Python.

**What bit me**

**One run is not a measurement.** Same code, same PDFs, same model, four minutes
apart: **10/10, then 9/10.** Nothing changed. The model is non-deterministic, so
a weak field description does not fail *always* — it fails *sometimes*, which is
worse. A bug that fails 20% of the time passes the test, passes the demo, passes
the pilot, and then fails in production where it cannot be reproduced.

The fix was an English edit — describing the vendor as the party *issuing* the
invoice and explicitly not the "bill to" party. Verified by three consecutive
clean runs, and by checking the other nine documents had not regressed.

Two honest caveats recorded at the time:

- Three clean runs do not prove a fix. They are consistent with a system that
  still fails 10% of the time. They reduce uncertainty; they do not remove it.
- **My benchmark was too easy.** 300-character, single-page, clean-text PDFs.
  Real invoices are 3,000+ characters with logos, terms and multiple addresses.
  A 10/10 on an easy benchmark measures the sample set, not the system.

**The wider lesson:** the target is not 100% accuracy — it is 100% *safety* with
a high automation rate. Route the confident cases through automatically, send
the rest to a human for twenty seconds. Nothing wrong gets in, and most of the
labour disappears. That is a sellable outcome; "our AI is 99% accurate" is not.

---

## Day 4 — Serving it over HTTP

**Built:** a FastAPI service wrapping the extractor. `/health`, `/ready`,
`POST /extract`.

**Core concepts**

- **`async def` with a blocking call stalls the whole server**, not just that
  request — health checks included. FastAPI runs a single-threaded event loop.
  A plain `def` handler is moved to a worker thread automatically, which is what
  blocking work needs. (Java: `async` is the Netty event loop; plain `def` is
  the servlet threadpool.) This only shows up under load.
- **Liveness is not readiness.** `/health` proves the process answers — which
  proves only that the process answers. `/ready` makes a real call to the model
  provider, so a wrong API key returns 503 and the load balancer stops sending
  work to an instance that cannot do any.
- One schema, three jobs: the extraction contract, the validator, and the
  documented response shape in the generated API docs.
- Error codes carry meaning. A scanned PDF with no text is the caller's problem
  (422). The model failing after retries is an upstream problem (502).

**Structure note:** at this point the code moved from flat modules into packages
by feature — `extraction/`, `api/` — each exporting a small public surface
through its `__init__.py`. Four days in, one file still imports the vendor SDK.

---

## Day 5 — Tool calling, and what an "agent" actually is

**Built:** an agent that answers questions by calling real functions — a live
weather lookup and a calculator — written by hand, no framework.

**Core concepts**

- **The model cannot do anything.** No internet, no files, no clock. Asked for
  the current temperature it says so, or invents one. It knows language, not today.
- Tool calling is an arrangement: I send the question **plus a menu** of things
  I am willing to do. The model replies with a *request* — a tool name and
  arguments. **It never executes anything.** My code runs the function and sends
  the result back as a new message. The model then answers.
- Three separate things, linked only by a name:
  - the function — my ordinary Python, never sent anywhere
  - the menu — plain data describing it, sent to the model
  - the dispatcher — a dictionary of what my code will *actually* run
- **The dispatcher is the security boundary.** Not the prompt. If the model asks
  for something not in that dictionary, the lookup fails and nothing happens.
  "Safety" means the dangerous thing is not on the menu — the model's good
  behaviour is irrelevant.
- **An agent is a loop**, not a personality: ask → wants a tool? → run it →
  feed the result back → ask again. It ends when the model replies with text
  instead of a request. Cap the rounds: a confused model loops forever and
  every lap is billed.
- Two shapes of tool use, and only one needs the loop:
  - *parallel* — "warmer in Pune or Bengaluru?" → both calls in one round
  - *sequential* — "temperature in Pune, doubled?" → round 2's arguments come
    from round 1's result. Impossible without looping.
- **Never `eval()` a string from the model.** It is untrusted input, and `eval`
  on it is arbitrary code execution. The calculator parses to a syntax tree and
  walks an **allow-list** of node types — a block-list is only a list of attacks
  you happened to think of.

**What bit me**

*The model skipped a tool it should have used, twice.* First it did arithmetic
in its head. Then, asked to compare two hill stations for coolness, it gave a
long travel answer with no live data at all — and ended by *offering* to fetch
the weather. It had considered the tool and declined.

Tool descriptions are prompt text, exactly like the Day 3 field descriptions.
Adding "use this for comparisons between places" and "ALWAYS use this for
arithmetic, your own is unreliable" made both tools fire.

But the way I found that out is the real lesson. I changed **two** things at
once — the description *and* a new system prompt — and it worked, so I could
not tell which one mattered. Testing each alone, one run each, said *neither
works alone, you need both*. **Running each five times said the opposite:**

    neither (original)      0/5
    new description only    5/5     <- this was the fix
    system prompt only      2/5     <- flaky, and it made answers worse
    both                    5/5

The single run did not just miss a failure — it produced the **opposite
conclusion**. I would have kept a change that does nothing.

So the system prompt came out again. Removing a change after measuring it is
harder than adding one; it feels like losing ground. I left a comment in the
code saying why, so I do not helpfully re-add it in six months.

**The wider lesson:** I optimised for "does it call the tool" because that is
countable. What I actually wanted was a useful answer — and the blunt system
prompt got the tool called while stripping out the travel advice that made the
first answer good. The thing you can measure is rarely the thing you want.

Underneath it all was a tool-design problem, not a prompting one: my tool
returns **weather**, the question needed **climate**. No wording fixes a tool
that returns the wrong kind of fact.

**Run**

```bash
uv run python scripts/stage1.py   # the model asks; nothing answers
uv run python scripts/stage2.py   # we answer; it finishes (has a known flaw — see the file)
uv run python scripts/stage3.py   # the loop
```

---

*Days 6–30 to follow.*
