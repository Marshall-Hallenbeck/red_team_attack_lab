# selectively taken from https://github.com/clong/MakeWindows10GreatAgain/blob/master/MakeWindows10GreatAgain.ps1
# Check to see if Anniversary Update is installed
if ([System.Environment]::OSVersion.Version.Build -lt 14393) {
  Write-Host "Build version 14393 or greater is required to continue. Exiting."
  Exit
}

# Import the registry keys
Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Importing registry keys..."
regedit /s C:\\make_windows_sorta_better.reg

# Remove OneDrive from the System
Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Removing OneDrive..."
taskkill /f /im OneDrive.exe
c:\Windows\SysWOW64\OneDriveSetup.exe /uninstall

# Remove all pinned items from Start Menu
# https://community.spiceworks.com/topic/post/7417573
Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Cleaning up start menu..."
(New-Object -Com Shell.Application).NameSpace('shell:::{4234d49b-0245-4df3-b780-3893943456e1}').Items()| foreach { ($_).Verbs() | ?{$_.Name.Replace('&', '') -match 'From "Start" UnPin|Unpin from Start'} | %{$_.DoIt()}  }

# Download and install ShutUp10
Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Downloading ShutUp10..."
[Net.ServicePointManager]::SecurityProtocol = "tls12, tls11, tls"
$shutUp10DownloadUrl = "https://dl5.oo-software.com/files/ooshutup10/OOSU10.exe"
$shutUp10RepoPath = "$home\AppData\Local\Temp\OOSU10.exe"
Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Installing ShutUp10..."
Invoke-WebRequest -Uri "$shutUp10DownloadUrl" -OutFile $shutUp10RepoPath
. $shutUp10RepoPath shutup10.cfg /quiet /force