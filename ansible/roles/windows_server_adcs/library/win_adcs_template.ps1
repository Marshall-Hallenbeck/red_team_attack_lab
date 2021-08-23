#!powershell

# Copyright: (c) 2018, Jordan Borean
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#Requires -Module Ansible.ModuleUtils.Legacy
#Requires -Module Ansible.ModuleUtils.SID
#AnsibleRequires -Become

$ErrorActionPreference = "Stop"

$params = Parse-Args -arguments $args -supports_check_mode $true
$check_mode = Get-AnsibleParam -obj $params -name "_ansible_check_mode" -type "bool" -default $false

$dacl = Get-AnsibleParam -obj $params -name "dacl" -type "list"
$group = Get-AnsibleParam -obj $params -name "group" -type "str"
$owner = Get-AnsibleParam -obj $params -name "owner" -type "str"
$templates = Get-AnsibleParam -obj $params -name "templates" -type "str" -failifempty $true

$result = @{
    changed = $false
}

# https://msdn.microsoft.com/en-us/library/cc230374.aspx
$mask_map = @{
    read_control = 0x00020000
    delete = 0x00010000
    write_dac = 0x00040000
    write_owner = 0x00080000
    read_prop = 0x00000010
    write_prop = 0x00000020
    create_child = 0x00000001
    delete_child = 0x00000002
    list_child = 0x00000004
    self_write = 0x00000008
    list_object = 0x00000080
    delete_tree = 0x00000040
    control_access = 0x00000100
}

Function ConvertTo-HashtableFromPsCustomObject($object) {
    if ($object -is [Hashtable]) {
        return ,$object
    }

    $hashtable = @{}
    $object | Get-Member -MemberType *Property | % {
        $value = $object.$($_.Name)
        if ($value -is [PSObject]) {
            $value = ConvertTo-HashtableFromPsCustomObject -object $value
        }
        $hashtable.$($_.Name) = $value
    }

    return ,$hashtable
}

Function ConvertTo-SDDL($owner, $group, $dacl) {
    $is_container = $false
    $is_ds = $false
    $flags = [System.Security.AccessControl.ControlFlags]::DiscretionaryAclPresent -bor [System.Security.AccessControl.ControlFlags]::DiscretionaryAclAutoInherited -bor [System.Security.AccessControl.ControlFlags]::DiscretionaryAclProtected -bor [System.Security.AccessControl.ControlFlags]::SelfRelative
    $parsed_owner = Convert-ToSID -account_name $owner
    $parsed_group = Convert-ToSID -account_name $group
    $sacl = $null
    if ($dacl) {
        $parsed_dacl = ConvertTo-Dacl -dacl $dacl
    } else {
        $parsed_dacl = $null
    }

    $security_descriptor = New-Object -TypeName System.Security.AccessControl.CommonSecurityDescriptor -ArgumentList @(
        $is_container, $is_ds, $flags, $parsed_owner, $parsed_group, $sacl, $parsed_dacl
    )
    $sddl = $security_descriptor.GetSddlForm([System.Security.AccessControl.AccessControlSections]::All)

    return $sddl
}

Function ConvertTo-Dacl($dacl) {
    $raw_acl = New-Object -TypeName System.Security.AccessControl.RawAcl -ArgumentList 0x4, $dacl.Count
    for ($i = 0; $i -lt $dacl.Count; $i++) {
        $sid = Convert-ToSID -account_name $dacl[$i].user
        $mask = 0
        $dacl[$i].rights | ForEach-Object { $mask = $mask -bor $mask_map[$_] }
        $qualifier = [System.Security.AccessControl.AceQualifier]::"$($dacl[$i].qualifier)"

        if ($dacl[$i].ContainsKey("type")) {
            $ace = New-ObjectAce -sid $sid -mask $mask -qualifier $qualifier -type $dacl[$i].type
        } else {
            $ace = New-CommonAce -sid $sid -mask $mask -qualifier $qualifier
        }
        $raw_acl.InsertAce($i, $ace)
    }
    $parsed_dacl = New-Object -TypeName System.Security.AccessControl.DiscretionaryAcl -ArgumentList $false, $false, $raw_acl

    return ,$parsed_dacl
}

Function New-CommonAce($sid, $mask, $qualifier) {
    $common_ace = New-Object -TypeName System.Security.AccessControl.CommonAce -ArgumentList @(
        [System.Security.AccessControl.AceFlags]::None,
        $qualifier,
        $mask,
        $sid,
        $false,
        $null
    )
    return $common_ace
}

Function New-ObjectAce($sid, $mask, $qualifier, $type) {
    $types = @{
        auto_enroll = "a05b8cc2-17bc-4802-a710-e7c15ab866a2"
        enroll = "0e10c968-78fb-11d2-90d4-00c04f79dc55"
    }

    $object_ace = New-Object -TypeName System.Security.AccessControl.ObjectAce -ArgumentList @(
        [System.Security.AccessControl.AceFlags]::None,
        $qualifier,
        $mask,
        $sid,
        [System.Security.AccessControl.ObjectAceFlags]::ObjectAceTypePresent,
        (New-Object -TypeName System.Guid -ArgumentList $types.$type),
        [System.Guid]::Empty,
        $false,
        $null
    )
    return $object_ace
}

$X509EnrollmentAuthFlags = @{
    X509AuthNone = 0
    X509AuthAnonymous = 1
    X509AuthKerberos = 2
    X509AuthUsername = 4
    X509AuthCertificate = 8
}

$X509CertificateEnrollmentContext = @{
    ContextUser = 0x1
    ContextMachine = 0x2
    ContextAdministratorForceMachine = 0x3
}

$X509EnrollmentPolicyLoadOption = @{
    LoadOptionDefault = 0
    LoadOptionCacheOnly = 1
    LoadOptionReload = 2
    LoadOptionRgisterForADChanges = 4
}

$CommitTemplateFlags = @{
    CommitFlagSaveTemplateGenerateOID = 1
    CommitFlagSaveTemplateUseCurrentOID = 2
    CommitFlagSaveTemplateOverwrite = 3
    CommitFlagDeleteTemplate = 4
}

$import_data = [System.Text.Encoding]::ASCII.GetBytes($templates)

$template_data = [xml]$templates
$ns = New-Object -TypeName System.Xml.XmlNamespaceManager -ArgumentList $template_data.NameTable
$ns.AddNamespace("p", $template_data.DocumentElement.NamespaceURI)
$template_names = $template_data.SelectNodes("//p:commonName", $ns) | ForEach-Object { $_.InnerText }
if ($template_name -isnot [array]) {
    $template_names = @($template_names)
}
$result.file_templates = $template_names

$parsed_dacl = @()
foreach ($entry in $dacl) {
    $hash_entry = ConvertTo-HashtableFromPsCustomObject -obj $entry
    $parsed_dacl += $hash_entry
}
try {
    $template_sddl = ConvertTo-SDDL -owner $owner -group $group -dacl $parsed_dacl
} catch {
    Fail-Json -obj $result -message "Failed to convert access control to SDDL string: $($_.Exception.Message)"
}
$result.sddl = $template_sddl

# first get a list of all existing templates so we can check whether to load it or not
$server = New-Object -ComObject X509Enrollment.CX509EnrollmentPolicyActiveDirectory
try {
    $server.Initialize($null, $null, $X509EnrollmentAuthFlags.X509AuthKerberos, $false, $X509CertificateEnrollmentContext.ContextUser)
} catch {
    Fail-Json -obj $result -message "Failed to initialise AD CS COM object: $($_.Exception.Message)"
}
try {
    $server.SetCredential(0, $X509EnrollmentAuthFlags.X509AuthKerberos, $null, $null)
} catch {
    Fail-Json -obj $result -message "Failed to set AD CS credential as Kerberos: $($_.Exception.Message)"
}
try {
    $server.LoadPolicy($X509EnrollmentPolicyLoadOption.LoadOptionReload)
} catch {
    Fail-Json -obj $result -message "Failed to set AD CS load policy reload: $($_.Exception.Message)"
}
try {
    $existing_templates = $server.GetTemplates() | ForEach-Object { $_.Property(1) } | Where-Object { $_ -in $template_names }
} catch {
    Fail-Json -obj $result -message "Failed to check if existing certificate template is present: $($_.Exception.Message)"
}
if ($existing_templates -isnot [array]) {
    $existing_templates = @($existing_templates)
}

$server = New-Object -ComObject X509Enrollment.CX509EnrollmentPolicyWebService
try {
    $server.InitializeImport($import_data)
} catch {
    Fail-Json -obj $result -message "Failed to import template data at '$path': $($_.Exception.Message)"
}
$templates = $server.GetTemplates()

$skipped_templates = @()
$added_templates = @()
foreach ($template in $templates) {
    $template_name = $template.Property(1)
    if ($template_name -in $existing_templates) {
        $skipped_templates += $template_name
    } else {
        $writeable_template = New-Object -ComObject X509Enrollment.CX509CertificateTemplateADWritable
        $writeable_template.Initialize($template)
        try {
            # seems to be a docs mismtach but 28 is the TemplatePropSecurityDescriptor enum value
            $writeable_template.Property(28) = $template_sddl
        } catch {
            Fail-Json -obj $result -message "Failed to set SDDL '$template_sddl' for template $($template_name): $($_.Exception.Message)"
        }

        if (-not $check_mode) {
            try {
                $writeable_template.Commit($CommitTemplateFlags.CommitFlagSaveTemplateGenerateOID, $null)
            } catch {
                Fail-Json -obj $result -message "Failed to commit template $($template_name): $($_.Exception.Message)"
            }
        }

        $result.changed = $true
        $added_templates += $template_name
    }
}
$result.skipped_templates = $skipped_templates
$result.added_templates = $added_templates

Exit-Json -obj $result