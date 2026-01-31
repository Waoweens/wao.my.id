-- PostgreSQL

CREATE TABLE guestbook (
	id SERIAL PRIMARY KEY,
	name TEXT NULL,
	message TEXT NOT NULL,
	created TIMESTAMPTZ NOT NULL DEFAULT now()
);
