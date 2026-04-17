CREATE INDEX profile_status_index IF NOT EXISTS
FOR (p:Profile)
ON (p.status);

DROP INDEX profile_id_index IF EXISTS;

CREATE CONSTRAINT profile_id_unique IF NOT EXISTS
FOR (p:Profile)
REQUIRE p.id IS UNIQUE;
