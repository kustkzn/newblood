// src/models/user.go
package models

type PasswordEntry struct {
	Service           string `json:"service"`
	EncryptedPassword string `json:"encrypted_password"`
}
