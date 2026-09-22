"""Generate ten synthetic invoice PDFs plus their ground truth.

Every company, person and number here is invented. Nothing is committed that
belongs to anyone, so these are safe to publish with the repo.

Each invoice plants a specific extraction trap — see TRAP in the data below.
Run:  uv run python scripts/make_samples.py
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent.parent / "samples"
W, H = A4


def _rupees(amount: float) -> str:
    """Indian grouping: 1,23,456.78 — not 123,456.78."""
    neg = amount < 0
    whole, frac = divmod(round(abs(amount) * 100), 100)
    s = str(whole)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    out = f"Rs. {s}.{frac:02d}"
    return f"-{out}" if neg else out


# ── the ten invoices ─────────────────────────────────────────────────────────
# TRAP names what each document is testing.
INVOICES = [
    dict(
        file="01_clean.pdf", style="standard", trap="none — baseline",
        vendor="Bharat Electronics Ltd", number="INV-2026-001",
        date="15/01/2026", total=12500.00, customer="Nilgiri Retail LLP",
        lines=[("Industrial relay 24V", 20, 500.00), ("Shipping", 1, 2500.00)],
    ),
    dict(
        file="02_number_in_footer.pdf", style="footer_number",
        trap="invoice number is in the footer, not the header",
        vendor="Sunrise Traders", number="BE/2026/0847",
        date="22/01/2026", total=8750.50, customer="Nilgiri Retail LLP",
        lines=[("Copper lug 16mm", 150, 45.00), ("Cable tie pack", 25, 80.02)],
    ),
    dict(
        file="03_bill_to_trap.pdf", style="big_bill_to",
        trap="customer name is far more prominent than the vendor name",
        vendor="Kaveri Industrial Supplies", number="INV-3391",
        date="05/02/2026", total=45200.00, customer="MAHALAXMI ENTERPRISES",
        lines=[("MCB 32A four pole", 40, 950.00), ("Enclosure IP65", 8, 900.00)],
    ),
    dict(
        file="04_ambiguous_date.pdf", style="standard",
        trap="date 03/04/2026 — is it 3 April or 4 March?",
        vendor="Deccan Logistics", number="TX-2026-0119",
        date="03/04/2026", total=3299.00, customer="Nilgiri Retail LLP",
        lines=[("Freight Bengaluru-Pune", 1, 2799.00), ("Handling", 1, 500.00)],
    ),
    dict(
        file="05_amount_due_label.pdf", style="amount_due",
        trap="labelled 'Amount Due', never 'Total'",
        vendor="Metro Office Solutions", number="AC-88213",
        date="11/02/2026", total=15750.00, customer="Nilgiri Retail LLP",
        lines=[("Desk 1200mm", 5, 2500.00), ("Chair ergonomic", 5, 650.00)],
    ),
    dict(
        file="06_many_totals.pdf", style="many_totals",
        trap="Subtotal / Tax / Previous Balance / Total Due — three decoys",
        vendor="Nandi Steel Works", number="SI-2026-447",
        date="28/02/2026", total=67890.25, customer="Nilgiri Retail LLP",
        lines=[("MS angle 50x50", 300, 190.00), ("Cutting charges", 1, 5000.00)],
    ),
    dict(
        file="07_indian_format.pdf", style="standard",
        trap="Rs. 1,23,456.78 — Indian digit grouping, not Western",
        vendor="Anand Textiles Pvt Ltd", number="GT-9920",
        date="07/03/2026", total=123456.78, customer="Nilgiri Retail LLP",
        lines=[("Cotton bolt 50m", 120, 950.00), ("Dyeing", 1, 9456.78)],
    ),
    dict(
        file="08_two_column.pdf", style="two_column",
        trap="two-column layout — tests whether text extraction scrambles order",
        vendor="Zenith Components", number="QP-2026-31",
        date="12/03/2026", total=9999.00, customer="Nilgiri Retail LLP",
        lines=[("Connector 8-pin", 90, 99.00), ("Assembly", 1, 1089.00)],
    ),
    dict(
        file="09_utility_bill.pdf", style="utility",
        trap="utility bill layout — no line items, different vocabulary",
        vendor="Konkan Power Distribution Co", number="KPDC-4471892",
        date="01/03/2026", total=4832.00, customer="Nilgiri Retail LLP",
        lines=[], units=1208, rate=4.00,
    ),
    dict(
        file="10_credit_note.pdf", style="credit_note",
        trap="credit note — the total is NEGATIVE",
        vendor="Sunrise Traders", number="CN-2026-014",
        date="18/03/2026", total=-2150.00, customer="Nilgiri Retail LLP",
        lines=[("Returned: Copper lug 16mm", 40, 45.00), ("Restocking credit", 1, 350.00)],
    ),
]


def _header(c: canvas.Canvas, inv: dict, *, vendor_small: bool = False) -> float:
    y = H - 25 * mm
    c.setFont("Helvetica-Bold", 9 if vendor_small else 17)
    c.drawString(20 * mm, y, inv["vendor"])
    c.setFont("Helvetica", 8)
    c.drawString(20 * mm, y - 6 * mm, "Plot 14, Industrial Estate, Bengaluru 560058")
    c.drawString(20 * mm, y - 10 * mm, "GSTIN 29AABCS1429B1ZQ")
    return y - 22 * mm


def _lines_table(c: canvas.Canvas, inv: dict, y: float) -> float:
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20 * mm, y, "Description")
    c.drawRightString(120 * mm, y, "Qty")
    c.drawRightString(150 * mm, y, "Rate")
    c.drawRightString(185 * mm, y, "Amount")
    c.line(20 * mm, y - 2 * mm, 185 * mm, y - 2 * mm)
    y -= 8 * mm
    c.setFont("Helvetica", 9)
    for desc, qty, rate in inv["lines"]:
        c.drawString(20 * mm, y, desc)
        c.drawRightString(120 * mm, y, str(qty))
        c.drawRightString(150 * mm, y, f"{rate:,.2f}")
        c.drawRightString(185 * mm, y, f"{qty * rate:,.2f}")
        y -= 6 * mm
    return y - 4 * mm


def build(inv: dict) -> None:
    c = canvas.Canvas(str(OUT / inv["file"]), pagesize=A4)
    style = inv["style"]

    if style == "two_column":
        # Vendor block on the left, meta block on the right, same vertical band.
        y = _header(c, inv)
        c.setFont("Helvetica", 9)
        c.drawString(20 * mm, y, "Bill To:")
        c.drawString(20 * mm, y - 5 * mm, inv["customer"])
        c.drawString(20 * mm, y - 10 * mm, "44 MG Road, Bengaluru 560001")
        c.drawRightString(185 * mm, y, f"Invoice No: {inv['number']}")
        c.drawRightString(185 * mm, y - 5 * mm, f"Date: {inv['date']}")
        c.drawRightString(185 * mm, y - 10 * mm, "Terms: Net 30")
        y = _lines_table(c, inv, y - 20 * mm)
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(185 * mm, y - 4 * mm, f"Total  {_rupees(inv['total'])}")

    elif style == "utility":
        y = _header(c, inv)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20 * mm, y, "ELECTRICITY BILL")
        y -= 8 * mm
        c.setFont("Helvetica", 9)
        for label, val in [
            ("Consumer Name", inv["customer"]),
            ("Consumer Number", "RR-88-4471892"),
            ("Bill Number", inv["number"]),
            ("Bill Date", inv["date"]),
            ("Billing Period", "01/02/2026 to 28/02/2026"),
            ("Units Consumed", f"{inv['units']} kWh"),
            ("Tariff", f"Rs. {inv['rate']:.2f} per kWh"),
            ("Fixed Charges", "Rs. 0.00"),
        ]:
            c.drawString(20 * mm, y, label)
            c.drawString(80 * mm, y, str(val))
            y -= 6 * mm
        c.line(20 * mm, y, 185 * mm, y)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(20 * mm, y - 8 * mm, f"Net Amount Payable   {_rupees(inv['total'])}")
        c.setFont("Helvetica", 8)
        c.drawString(20 * mm, y - 18 * mm, "Pay by 20/03/2026 to avoid a late payment surcharge.")

    elif style == "credit_note":
        y = _header(c, inv)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(20 * mm, y, "CREDIT NOTE")
        c.setFont("Helvetica", 9)
        c.drawRightString(185 * mm, y, f"Credit Note No: {inv['number']}")
        c.drawRightString(185 * mm, y - 5 * mm, f"Date: {inv['date']}")
        c.drawString(20 * mm, y - 8 * mm, f"Issued to: {inv['customer']}")
        c.drawString(20 * mm, y - 13 * mm, "Against invoice BE/2026/0847")
        y = _lines_table(c, inv, y - 24 * mm)
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(185 * mm, y - 4 * mm, f"Total Credit  {_rupees(inv['total'])}")
        c.setFont("Helvetica", 8)
        c.drawRightString(185 * mm, y - 12 * mm, "This amount is credited to your account.")

    else:
        small = style == "big_bill_to"
        y = _header(c, inv, vendor_small=small)

        if style == "big_bill_to":
            c.setFont("Helvetica-Bold", 20)
            c.drawString(20 * mm, y, inv["customer"])
            c.setFont("Helvetica", 9)
            c.drawString(20 * mm, y - 7 * mm, "12 Residency Road, Bengaluru 560025")
            y -= 18 * mm
        else:
            c.setFont("Helvetica", 9)
            c.drawString(20 * mm, y, f"Bill To: {inv['customer']}")
            y -= 10 * mm

        c.setFont("Helvetica", 9)
        if style != "footer_number":
            c.drawRightString(185 * mm, y + 4 * mm, f"Invoice No: {inv['number']}")
        c.drawRightString(185 * mm, y - 1 * mm, f"Date: {inv['date']}")

        y = _lines_table(c, inv, y - 12 * mm)

        if style == "many_totals":
            sub = sum(q * r for _, q, r in inv["lines"])
            tax = round(inv["total"] - sub - 4000.00, 2)
            c.setFont("Helvetica", 10)
            c.drawRightString(185 * mm, y, f"Subtotal        {_rupees(sub)}")
            c.drawRightString(185 * mm, y - 6 * mm, f"GST 18%         {_rupees(tax)}")
            c.drawRightString(185 * mm, y - 12 * mm, f"Previous Balance   {_rupees(4000.00)}")
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(185 * mm, y - 20 * mm, f"Total Due   {_rupees(inv['total'])}")
        elif style == "amount_due":
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(185 * mm, y - 4 * mm, f"Amount Due   {_rupees(inv['total'])}")
        else:
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(185 * mm, y - 4 * mm, f"Total   {_rupees(inv['total'])}")

        if style == "footer_number":
            c.setFont("Helvetica", 7)
            c.drawString(20 * mm, 15 * mm,
                         f"Ref {inv['number']} | Terms Net 30 | E&OE | Page 1 of 1")

    c.showPage()
    c.save()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    truth = {}
    for inv in INVOICES:
        build(inv)
        truth[inv["file"]] = {
            "invoice_number": inv["number"],
            "invoice_date": inv["date"],
            "vendor_name": inv["vendor"],
            "total_amount": inv["total"],
            "_trap": inv["trap"],
        }
    (OUT / "ground_truth.json").write_text(json.dumps(truth, indent=2))
    print(f"wrote {len(INVOICES)} PDFs + ground_truth.json to {OUT}")


if __name__ == "__main__":
    main()
