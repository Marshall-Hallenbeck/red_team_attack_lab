# Constrained & Unconstrained Delegation
Login to our kali host
```
vagrant ssh kali
```
## Find Delegation via Impacket
```
impacket-findDelegation -dc-ip 10.0.1.10 'attacklab.local/Phoebe Chillax:summer2021!'
```
Output:
```
AccountName         AccountType  DelegationType  DelegationRightsTo
------------------  -----------  --------------  -----------------------------------------
Unconstrained User  Person       Unconstrained   N/A
Constrained User    Person       Constrained     CIFS/dc01.attacklab.local/attacklab.local
Constrained User    Person       Constrained     CIFS/dc01.attacklab.local
Constrained User    Person       Constrained     CIFS/dc01
```

## Find Unconstrained Delegation via Crackmapexec
TODO: Finish documenting this

Requires both a host to target (can be any place the user can login to) and --kdcHost parameter
```
crackmapexec ldap 10.0.1.10 -u 'Phoebe Chillax' -p 'summer2021!' --trusted-for-delegation --kdcHost 10.0.1.10
```
Output:
```
LDAP        10.0.1.10       389    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:attacklab.local) (signing:True) (SMBv1:False)
LDAP        10.0.1.10       389    DC01             [+] attacklab.local\Phoebe Chillax:summer2021!
LDAP        10.0.1.10       389    DC01             Unconstrained User
LDAP        10.0.1.10       389    DC01             DC01$

```

## Find Delegation via Powershell ActiveDirectory Module
TODO: Finish documenting this
```
Import-Module ActiveDirectory
Get-ADComputer -Filter {(TrustedForDelegation -eq $True) -AND (PrimaryGroupID -eq 515) } -Properties `TrustedForDelegation,TrustedToAuthForDelegation,servicePrincipalName,Description
```