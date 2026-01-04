// Package routes содержит HTTP-обработчики
package routes

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"password-vault/crypto"
	"password-vault/database"
	"strconv"

	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
)

// Register регистрирует нового пользователя
func Register(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	if req.Username == "" || req.Password == "" {
		http.Error(w, "Username and password required", http.StatusBadRequest)
		return
	}

	hash, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		http.Error(w, "Internal error", http.StatusInternalServerError)
		return
	}

	_, err = database.DB.Exec("INSERT INTO users (username, password_hash) VALUES (?, ?)", req.Username, string(hash))
	if err != nil {
		http.Error(w, "Username already exists", http.StatusConflict)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

// Login аутентифицирует пользователя и выдаёт JWT
func Login(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	var userID int
	var storedHash string
	err := database.DB.QueryRow("SELECT id, password_hash FROM users WHERE username = ?", req.Username).
		Scan(&userID, &storedHash)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Invalid credentials", http.StatusUnauthorized)
		} else {
			http.Error(w, "Database error", http.StatusInternalServerError)
		}
		return
	}

	if err := bcrypt.CompareHashAndPassword([]byte(storedHash), []byte(req.Password)); err != nil {
		http.Error(w, "Invalid credentials", http.StatusUnauthorized)
		return
	}

	// Генерация JWT
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user_id": userID,
	})
	tokenString, err := token.SignedString(jwtKey)
	if err != nil {
		http.Error(w, "Token generation failed", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"token": tokenString})
}

// SavePassword — БЕЗОПАСНЫЙ: шифрует пароль и использует параметризованный запрос
func SavePassword(w http.ResponseWriter, r *http.Request) {
	if r.Method == "OPTIONS" {
		return
	}

	userIDStr := r.Header.Get("X-User-ID")
	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		http.Error(w, "Invalid user", http.StatusUnauthorized)
		return
	}

	var req struct {
		Service  string `json:"service"`
		Password string `json:"password"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	if req.Service == "" || req.Password == "" {
		http.Error(w, "Service and password required", http.StatusBadRequest)
		return
	}

	// Шифруем пароль
	encrypted, err := crypto.EncryptPassword(req.Password)
	if err != nil {
		http.Error(w, "Encryption failed", http.StatusInternalServerError)
		return
	}

	// ✅ Безопасный запрос
	_, err = database.DB.Exec(
		"INSERT INTO passwords (user_id, service, encrypted_password) VALUES (?, ?, ?)",
		userID, req.Service, encrypted,
	)
	if err != nil {
		log.Printf("Save error: %v", err)
		http.Error(w, "Save failed", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

// ViewPassword — УЯЗВИМЫЙ: service подставляется напрямую в SQL
func ViewPassword(w http.ResponseWriter, r *http.Request) {
	if r.Method == "OPTIONS" {
		return
	}

	userIDStr := r.Header.Get("X-User-ID")
	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		http.Error(w, "Invalid user", http.StatusUnauthorized)
		return
	}

	service := r.URL.Query().Get("service")
	if service == "" {
		http.Error(w, "service parameter required", http.StatusBadRequest)
		return
	}

	// 🔥 УЯЗВИМОСТЬ: прямая подстановка service в SQL
	query := fmt.Sprintf("SELECT encrypted_password FROM passwords WHERE user_id = %d AND service = '%s'", userID, service)
	rows, err := database.DB.Query(query)
	if err != nil {
		log.Printf("SQL error: %v", err)
		http.Error(w, "Query error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	if rows.Next() {
		var encryptedHex string
		if err := rows.Scan(&encryptedHex); err != nil {
			http.Error(w, "Scan error", http.StatusInternalServerError)
			return
		}

		// Расшифровка
		plaintext, err := crypto.DecryptPassword(encryptedHex)
		if err != nil {
			log.Printf("Decryption failed: %v", err)
			http.Error(w, "Decryption error", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"password": plaintext})
	} else {
		http.Error(w, "Password not found", http.StatusNotFound)
	}
}
