package main

import ("database/sql"; "crypto/rand")

func s(db *sql.DB, id string) {
	_, _ = db.Query("SELECT * FROM u WHERE id = ?", id)
	b := make([]byte, 16)
	_, _ = rand.Read(b)
}
