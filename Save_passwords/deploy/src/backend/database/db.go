// Package database управляет подключением к MySQL и инициализацией схемы
package database

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

	_ "github.com/go-sql-driver/mysql"
)

var DB *sql.DB

// InitDB инициализирует соединение с базой данных и создаёт таблицы
func InitDB() {
	host := os.Getenv("DB_HOST")
	user := os.Getenv("DB_USER")
	pass := os.Getenv("DB_PASS")
	name := os.Getenv("DB_NAME")

	if host == "" || user == "" || pass == "" || name == "" {
		log.Fatal("Missing database environment variables (DB_HOST, DB_USER, DB_PASS, DB_NAME)")
	}

	dsn := fmt.Sprintf("%s:%s@tcp(%s:3306)/%s?parseTime=true&multiStatements=true", user, pass, host, name)

	var err error
	maxRetries := 10
	for i := 0; i < maxRetries; i++ {
		DB, err = sql.Open("mysql", dsn)
		if err != nil {
			log.Printf("❌ DB open error (attempt %d/%d): %v", i+1, maxRetries, err)
			time.Sleep(2 * time.Second)
			continue
		}

		// Проверяем подключение
		if err = DB.Ping(); err == nil {
			log.Println("✅ Successfully connected to MySQL database")
			createTables()
			return
		}

		log.Printf("❌ DB ping failed (attempt %d/%d): %v", i+1, maxRetries, err)
		DB.Close()
		time.Sleep(2 * time.Second)
	}

	log.Fatalf("❌ Failed to connect to database after %d attempts", maxRetries)
}

// createTables создаёт таблицы users и passwords (по одной, чтобы избежать multi-query ошибок)
func createTables() {
	// Таблица пользователей
	queryUsers := `
		CREATE TABLE IF NOT EXISTS users (
			id INT AUTO_INCREMENT PRIMARY KEY,
			username VARCHAR(255) UNIQUE NOT NULL,
			password_hash VARCHAR(255) NOT NULL
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
	`

	_, err := DB.Exec(queryUsers)
	if err != nil {
		log.Fatalf("❌ Failed to create 'users' table: %v", err)
	}

	// Таблица паролей
	queryPasswords := `
		CREATE TABLE IF NOT EXISTS passwords (
			id INT AUTO_INCREMENT PRIMARY KEY,
			user_id INT NOT NULL,
			service VARCHAR(255) NOT NULL,
			encrypted_password TEXT NOT NULL,
			FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
	`

	_, err = DB.Exec(queryPasswords)
	if err != nil {
		log.Fatalf("❌ Failed to create 'passwords' table: %v", err)
	}

	log.Println("✅ Tables 'users' and 'passwords' are ready")
}
