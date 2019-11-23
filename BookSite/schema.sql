-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS manager;
DROP TABLE IF EXISTS bookData;

CREATE TABLE manager (
  id INTEGER PRIMARY KEY,
  managername TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE bookData (
  id INTEGER PRIMARY KEY,
  manager_id INTEGER NOT NULL,
  bookTitle TEXT NOT NULL,
  author TEXT NOT NULL,
  publisher TEXT NOT NULL,
  price INTEGER,
  purchaseDate TEXT,
  memo TEXT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (manager_id) REFERENCES manager (id)
);
