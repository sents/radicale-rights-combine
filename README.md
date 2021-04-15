# What does this do?
This is a radicale plugin to use multiple radicale rights plugins at once.
The plugin will grant access to a path whenever **any** of the chosen plugins grants access.
The rights plugins that are to be used are specified in the types option in the rights section of the radicale config.
The plugin options for the specified rights are given in the same way you would write them if you were only using one plugin (for now I am hoping that there are no conflicting options). Because I needed it there is also a `follow_symlinks` flag to make the rights plugins check the destination path for access rights
instead of the link when there are symlinks in a users collection

Here is an example using the radicale\_rights\_ldap plugin with the from\_file builtin rights provider.
In `/etc/radicale/conf`:
```
[rights]

type = radicale-rights-combine
types = radicale_rights_ldap, from_file
# File for from_file
file = /etc/radicale/rights

# radicale_rights_ldap configuration
# LDAP server url, with protocol and optionally port.
ldap_url = ldap://ldapserver:389

# LDAP user base path
user_base = ou=People,dc=domain

# LDAP group base path
group_base = ou=Groups,dc=domain

# LDAP user bottom level dn path attribute
user_attribute = uid

# LDAP user bottom level dn path attribute
group_attribute = cn

# LDAP dn for login
ldap_binddn = uid=admin,dc=Domain

# LDAP Password for ldap_binddn
ldap_password = swordfish1234

# LDAP filter for which users get managed by the plugin
ldap_filter = memberOf=cn=radicaleUsers,ou=Groups,dc=Domain

# LDAP scope of the search, default is SUBTREE
ldap_scope = LEVEL
```
In `/etc/radicale/rights`:
```
# from_file configuration
# The user "admin" can read and write any collection.
[admin]
user = admin
collection = .*
permission = rw

# Block access for the user "user" to everything.
[block]
user = user
collection = .*
permission =

# Authenticated users can read and write their own collections.
[owner-write]
user = .+
collection = %(login)s(/.*)?
permission = rw

# Everyone can read the root collection
[read]
user = .*
collection =
permission = r
```
