CREATE CONSTRAINT profile_mail_unique IF NOT EXISTS
FOR (p:Profile)
REQUIRE p.mail IS UNIQUE;