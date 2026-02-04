-- PostgreSQL

CREATE TABLE guestbook (
	id SERIAL PRIMARY KEY,
	name TEXT NULL,
	message TEXT NOT NULL,
	created TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE guestbook_reports (
	id SERIAL PRIMARY KEY,
	entry_id INTEGER NOT NULL REFERENCES guestbook(id) ON DELETE CASCADE,
	reason TEXT NOT NULL,
	created TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE listening_history (
	id SERIAL PRIMARY KEY,
	track_id TEXT NOT NULL,
	track JSONB NOT NULL,
	listened_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
