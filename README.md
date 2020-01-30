# TA-dnslookup
Splunk add on to do "any" DNS lookup

By default Splunk can only do IP <> FQDN lookups, with this TA you can do any kind of dns lookup that you want.

# Usage
After installation of the TA you will get a custom command with a couple of options. \
``` | dnslookup field=<field> [[r=<record>] [sr=<sub-record>]]
<field>       = The name of the field that contains the info to do the DNS lookup on
<record>      = The DNS record to get.
<sub-record>  = The sub-record to get.
```
