package crypto

import (
	"crypto/aes"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"math/big"
)

// ============================================================================
var (
	secretKey []byte
	p         *big.Int
	a         *big.Int
	b         *big.Int
	Gx        *big.Int
	Gy        *big.Int
)

func Init(key string) {
	secretKey = []byte(key)
	p, _ = new(big.Int).SetString("340282366920938463463374607431767211629", 10)

	a = big.NewInt(3)
	b = big.NewInt(9)

	Gx, _ = new(big.Int).SetString("115423119360425591167519108349272384530", 10)
	Gy, _ = new(big.Int).SetString("26739966749909391609878417468245881872", 10)
}

// ============================================================================

func fromHex(s string) *big.Int {
	n, ok := new(big.Int).SetString(s, 16)
	if !ok {
		panic("invalid hex in curve parameters: " + s)
	}
	return n
}

type Curve struct {
	P *big.Int
	A *big.Int
	B *big.Int
}

type Point struct {
	X, Y *big.Int
}

var Zero = &Point{X: nil, Y: nil}

func mod(x, p *big.Int) *big.Int {
	if x.Sign() < 0 {
		x = new(big.Int).Add(x, p)
	}
	return new(big.Int).Mod(x, p)
}

func (c *Curve) Add(p1, p2 *Point) *Point {
	if p1.X == nil {
		return p2
	}
	if p2.X == nil {
		return p1
	}

	x1m := mod(p1.X, c.P)
	x2m := mod(p2.X, c.P)
	y1m := mod(p1.Y, c.P)
	y2m := mod(p2.Y, c.P)

	if x1m.Cmp(x2m) == 0 {
		y1Neg := mod(new(big.Int).Neg(y1m), c.P)
		if y2m.Cmp(y1Neg) == 0 {
			return Zero
		}

		return c.Double(p1)
	}

	yDiff := mod(new(big.Int).Sub(y2m, y1m), c.P)
	xDiff := mod(new(big.Int).Sub(x2m, x1m), c.P)
	xDiffInv := new(big.Int).ModInverse(xDiff, c.P)
	if xDiffInv == nil {
		return Zero
	}
	lambda := mod(new(big.Int).Mul(yDiff, xDiffInv), c.P)

	x3 := mod(new(big.Int).Sub(
		new(big.Int).Sub(new(big.Int).Mul(lambda, lambda), x1m),
		x2m,
	), c.P)

	y3 := mod(new(big.Int).Sub(
		new(big.Int).Mul(lambda, mod(new(big.Int).Sub(x1m, x3), c.P)),
		y1m,
	), c.P)

	return &Point{X: x3, Y: y3}
}

func (c *Curve) Double(p *Point) *Point {
	if p.X == nil || mod(p.Y, c.P).Sign() == 0 {
		return Zero
	}

	xm := mod(p.X, c.P)
	ym := mod(p.Y, c.P)

	x2 := new(big.Int).Mul(xm, xm)
	num := mod(new(big.Int).Add(new(big.Int).Mul(big.NewInt(3), x2), c.A), c.P)
	den := mod(new(big.Int).Mul(big.NewInt(2), ym), c.P)
	denInv := new(big.Int).ModInverse(den, c.P)
	if denInv == nil {
		return Zero
	}
	lambda := mod(new(big.Int).Mul(num, denInv), c.P)

	x3 := mod(new(big.Int).Sub(new(big.Int).Mul(lambda, lambda), new(big.Int).Mul(big.NewInt(2), xm)), c.P)

	y3 := mod(new(big.Int).Sub(
		new(big.Int).Mul(lambda, mod(new(big.Int).Sub(xm, x3), c.P)),
		ym,
	), c.P)

	return &Point{X: x3, Y: y3}
}

func (c *Curve) ScalarMult(k *big.Int, P *Point) *Point {
	if k.Sign() <= 0 {
		return Zero
	}
	k = new(big.Int).Mod(k, c.P)
	Q := Zero
	R := P
	n := new(big.Int).Set(k)
	for n.Sign() > 0 {
		if n.Bit(0) == 1 {
			Q = c.Add(Q, R)
		}
		R = c.Double(R)
		n.Rsh(n, 1)
	}
	return Q
}

func pointToAESKey(P *Point) []byte {
	if P.X == nil {
		panic("cannot derive key from infinity point")
	}
	h := sha256.New()
	h.Write(P.X.Bytes())
	h.Write(P.Y.Bytes())
	return h.Sum(nil)
}

func aesECBEncrypt(key, plaintext []byte) ([]byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}

	n := len(plaintext)
	blockSize := aes.BlockSize
	padding := blockSize - n%blockSize
	padded := make([]byte, n+padding)
	copy(padded, plaintext)
	for i := n; i < len(padded); i++ {
		padded[i] = byte(padding)
	}
	ciphertext := make([]byte, len(padded))
	for i := 0; i < len(padded); i += blockSize {
		block.Encrypt(ciphertext[i:i+blockSize], padded[i:i+blockSize])
	}
	return ciphertext, nil
}

func aesECBDecrypt(key, ciphertext []byte) ([]byte, error) {
	if len(ciphertext)%aes.BlockSize != 0 {
		return nil, fmt.Errorf("ciphertext length not multiple of block size")
	}
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}
	plaintext := make([]byte, len(ciphertext))
	for i := 0; i < len(ciphertext); i += aes.BlockSize {
		block.Decrypt(plaintext[i:i+aes.BlockSize], ciphertext[i:i+aes.BlockSize])
	}

	padding := int(plaintext[len(plaintext)-1])
	if padding < 1 || padding > aes.BlockSize {
		return nil, fmt.Errorf("invalid padding")
	}
	return plaintext[:len(plaintext)-padding], nil
}

func EncryptPassword(password string) (string, error) {
	kBytes := sha256.Sum256([]byte(secretKey))
	k := new(big.Int).SetBytes(kBytes[:])

	curve := &Curve{P: p, A: a, B: b}
	G := &Point{X: Gx, Y: Gy}
	P := curve.ScalarMult(k, G)

	aesKey := pointToAESKey(P)
	ciphertext, err := aesECBEncrypt(aesKey, []byte(password))
	if err != nil {
		return "", err
	}
	return hex.EncodeToString(ciphertext), nil // ← string
}

func DecryptPassword(ciphertextHex string) (string, error) {
	ciphertext, err := hex.DecodeString(ciphertextHex)
	if err != nil {
		return "", err
	}

	kBytes := sha256.Sum256([]byte(secretKey))
	k := new(big.Int).SetBytes(kBytes[:])

	curve := &Curve{P: p, A: a, B: b}
	G := &Point{X: Gx, Y: Gy}
	P := curve.ScalarMult(k, G)

	aesKey := pointToAESKey(P)
	plaintext, err := aesECBDecrypt(aesKey, ciphertext)
	if err != nil {
		return "", err
	}
	return string(plaintext), nil
}
