# TA-dnslookup
Splunk add on to do "any" DNS lookup

By default Splunk can only do IP <> FQDN lookups, with this TA you can do any kind of dns lookup that you want.

# Usage
After installation of the TA you will get a custom command with a couple of options. 
``` 
| dnslookup field=<field> [[r=<record>] [sr=<sub-record>]]
<field>       = The name of the field that contains the info to do the DNS lookup on
<record>      = The DNS record to get (MX/TXT/CNAME/...).
<sub-record>  = The sub-record to get (DMARC/SPF/...)
```
# Examples
## Example 1
Get the MX records voor gmail.com
### Query:
```
| makeresults
| eval src="gmail.com"
| dnslookup field=src r=mx
| fields - _time
```
### Result:
![Example 1](/static/example_01.png?raw=true "Results for example 1")

## Example 2
Get the TXT records of google.com
### Query:
```
| makeresults
| eval src="google.com"
| dnslookup field=src r=txt
| fields - _time
```
### Result:
![Example 2](/static/example_02.png?raw=true "Results for example 2")

## Example 3
Get the SPF record for gmail.com
### Query:
```
| makeresults
| eval src="gmail.com"
| dnslookup field=src r=txt sr=spf
| fields - _time
```
### Result:
![Example 3](/static/example_03.png?raw=true "Results for example 3")

## Example 4
Get the complete SPF record for gmail.com (follow the redirects and includes)
### Query:
```
| makeresults
| eval src="gmail.com"
| dnslookup field=src r=txt sr=spf-full
| fields - _time
```
### Result:
![Example 4](/static/example_04.png?raw=true "Results for example 4")
