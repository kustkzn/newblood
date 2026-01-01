// backend/main.go
package main

import (
	"log"
	"net/http"
	"os"

	"password-vault/crypto"
	"password-vault/database"
	"password-vault/routes"
)

func main() {
	key := os.Getenv("SECRET_KEY")
	if key == "" {
		log.Fatal("SECRET_KEY not set")
	}
	crypto.Init(key)

	database.InitDB()

	// API routes
	http.HandleFunc("/register", routes.Register)
	http.HandleFunc("/login", routes.Login)
	http.HandleFunc("/save", routes.AuthMiddleware(routes.SavePassword))
	http.HandleFunc("/view", routes.AuthMiddleware(routes.ViewPassword))

	// Serve frontend
	fs := http.FileServer(http.Dir("/root/frontend/"))
	http.Handle("/", http.StripPrefix("/", fs))

	log.Println("Server starting on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
