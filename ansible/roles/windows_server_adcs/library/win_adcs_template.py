#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Jordan Borean
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: win_adcs_template
short_description: Imports a certificate template into AD CS.
description:
- This module will import a template provided by the I(template) option into
  the local AD CS instance.
- This template must be manually exported from AD CS as it is follows a
  particular format, see U(https://blogs.technet.microsoft.com/pki/2009/09/25/introducing-certificate-template-api/)
  for a guide on how to do that.
options:
  dacl:
    description:
    - A list of DACL entries to apply to the imported template.
    - This is only applied if the template has not already been imported.
    suboptions:
      user:
        description:
        - The user or SID to apply the DACL entry to.
        required: yes
      rights:
        description:
        - A list of rights to apply for the DACL entry.
        required: yes
        choices:
        - read_control
        - delete
        - write_dac
        - write_owner
        - read_prop
        - write_prop
        - create_child
        - delete_child
        - list_child
        - self_write
        - list_object
        - delete_tree
        - control_access
      type:
        description:
        - If the ACE entry is an object ACE, this is the type of object.
        choices:
        - enroll
        - auto_enroll
      qualifier:
        description:
        - The value that specified the ACE qualifier.
        options:
        - AccessAllowed
        - AccessDenied
        - SystemAlarm
        - SystemAudit
  group:
    description:
    - The account or SID of the group applied to the template's security
      descriptor.
    - This is only applied if the template is imported.
  owner:
    description:
    - The account or SID of the owner applied to the template's security
      descriptor.
    - This is only applied if the template is imported.
  templates:
    description:
    - The XML string that defines the template(s) to import.
    - This value is from the exported template from an existing AD CS server.
    required: yes
notes:
- This module requires Ansible become to run, if become is not set on the
  Ansible task explicitly, then the C(SYSTEM) account will be used.
- This module will import the template to the default AD CS server that is
  configured on the remote host.
- This module uses components that are only available on Server 2012 or newer.
author:
- Jordan Borean (@jborean93)
'''

EXAMPLES = r'''
- name: import AD CS template
  win_adcs_template:
    templates: '{{ lookup("template", "certificate.xml.j2") }}'
    dacl:
    - user: Enterprise Admins
      rights:
      - create_child
      - delete_child
      - list_child
      - self_write
      qualifier: AccessAllowed
    - user: Domain Computers
      rights:
      - control_access
      type: auto_enroll
      qualifier: AllowAccess
    - user: Domain Computers
      rights:
      - read_prop
      - write_prop
      - control_access
      type: enroll
      qualifier: AllowAccess
    owner: Enterprise Admins
    group: Enterprise Admins
'''

RETURN = r'''
added_templates:
  description: A list of templates that were added
  returned: always
  type: list
  sample: ["Template2"]
templates:
  description: A list of templates that were read in the I(templates) XML
    string
  returned: always
  type: list
  sample: ["Template1", "Template2", "Template3"]
sddl:
  description: The SDDL string that will be applied to the imported templates
  returned: always
  type: str
  sample: 'O:EAG:EAD:PAI(A;;CCDCLCSW;;;EA)(OA;;RPWPCR;0e10c968-78fb-11d2-90d4-00c04f79dc55;;DC)(OA;;CR;a05b8cc2-17bc-4802-a710-e7c15ab866a2;;DC)'
skipped_templates:
  description: A list of templates that were not added as they were already
    present
  returned: always
  type: list
  sample: ["Template1", "Template3"]
'''
