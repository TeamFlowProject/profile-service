CREATE INDEX profile_id_index IF NOT EXISTS
FOR (p:Profile)
ON (p.id);