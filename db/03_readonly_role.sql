-- The login the AGENT uses. It cannot write. That is the point.
--
-- Layers 1 and 2 (the menu, the dispatcher) are my code, and my code has
-- bugs. This layer is the database refusing, which is why it is the one
-- that actually holds.

DROP ROLE IF EXISTS sprint_app;
CREATE ROLE sprint_app LOGIN PASSWORD 'app_dev_password';

-- Start from nothing, then grant only what is needed.
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM sprint_app;
REVOKE ALL ON SCHEMA public FROM sprint_app;

GRANT CONNECT ON DATABASE sprint TO sprint_app;
GRANT USAGE   ON SCHEMA public   TO sprint_app;   -- see the schema...
GRANT SELECT  ON ALL TABLES IN SCHEMA public TO sprint_app;  -- ...read only

-- Tables created later are read-only for this role too, automatically.
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO sprint_app;

-- Belt and braces: even a write that somehow got granted is refused.
ALTER ROLE sprint_app SET default_transaction_read_only = on;

-- A runaway query cannot pin the database.
ALTER ROLE sprint_app SET statement_timeout = '5s';
