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
![Example 1](/static/example_01.jpg?raw=true "Results for example 1")

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
![Example 2](/static/example_02.jpg?raw=true "Results for example 2")

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
![Example 3](/static/example_03.jpg?raw=true "Results for example 3")

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
![Example 4](/static/example_04.jpg?raw=true "Results for example 4")

# Performance
I did a small test on my VM with the top 100 domains based on data traffic, and requested all 'A' and 'AAAA' records for each of them.
### Query:
```
| makeresults
| eval src="google.com,youtube.com,facebook.com,baidu.com,wikipedia.org,twitter.com,yahoo.com,pornhub.com,instagram.com,xvideos.com,yandex.ru,ampproject.org,xnxx.com,amazon.com,live.com,vk.com,netflix.com,qq.com,whatsapp.com,mail.ru,reddit.com,yahoo.co.jp,google.com.br,bing.com,ok.ru,xhamster.com,sogou.com,ebay.com,bit.ly,twitch.tv,linkedin.com,samsung.com,sm.cn,msn.com,office.com,globo.com,taobao.com,pinterest.com,google.de,microsoft.com,accuweather.com,naver.com,aliexpress.com,fandom.com,quora.com,github.com,imdb.com,uol.com.br,docomo.ne.jp,youporn.com,bbc.co.uk,microsoftonline.com,paypal.com,google.fr,yidianzixun.com,wordpress.com,news.google.com,sohu.com,duckduckgo.com,google.co.uk,10086.cn,iqiyi.com,booking.com,amazon.co.jp,cricbuzz.com,taboola.com,amazon.de,cnn.com,jd.com,apple.com,google.it,bilibili.com,google.co.jp,livejasmin.com,tmall.com,news.yahoo.co.jp,youtu.be,tribunnews.com,amazon.co.uk,chaturbate.com,google.co.in,craigslist.org,imgur.com,bbc.com,fc2.com,tsyndicate.com,redtube.com,tumblr.com,foxnews.com,rakuten.co.jp,google.es,outbrain.com,discordapp.com,amazon.in,crptgate.com,weather.com,toutiao.com,youku.com,adobe.com,news.yandex.ru", src=split(src,",")
| mvexpand src
| dnslookup field=src 
| fields - _time
```
### Result:
![Performance](/static/performance.jpg?raw=true "Small scale performance test")


# Credits
This app can only work thanks to [dnspython](http://www.dnspython.org/)
