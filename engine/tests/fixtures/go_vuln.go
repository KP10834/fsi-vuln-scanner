package main

import ("fmt"; "math/rand"; "os/exec"; "crypto/tls"; "net/http")

func v(id string) {
	q := fmt.Sprintf("SELECT * FROM u WHERE id = %s", id)
	_ = exec.Command("sh", "-c", "echo "+id)
	token := rand.Intn(999999)
	_ = &tls.Config{InsecureSkipVerify: true}
	_ = http.ListenAndServe(":8080", nil)
	_ = q; _ = token
}
