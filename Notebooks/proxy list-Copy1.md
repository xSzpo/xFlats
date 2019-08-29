

```python
x=["78.141.221.103:10001",
"78.141.221.103:10002",
"78.141.221.103:10003",
"78.141.221.103:10004",
"78.141.221.103:10005",
"78.141.221.103:10006",
"78.141.221.103:10007",
"78.141.221.103:10008",
"78.141.221.103:10009",
"78.141.221.103:10010",
"78.141.221.103:10011",
"78.141.221.103:10012",
"78.141.221.103:10013",
"78.141.221.103:10014",
"78.141.221.103:10015",
"78.141.221.103:10016",
"78.141.221.103:10017",
"78.141.221.103:10018",
"78.141.221.103:10019",
"78.141.221.103:10020",
"78.141.221.103:10021",
"78.141.221.103:10022",
"78.141.221.103:10023",
"78.141.221.103:10024",
"78.141.221.103:10025",
"78.141.221.103:10026",
"78.141.221.103:10027",
"78.141.221.103:10028",
"78.141.221.103:10029",
"78.141.221.103:10030",
"78.141.221.103:10031",
"78.141.221.103:10032",
"78.141.221.103:10033",
"78.141.221.103:10034",
"78.141.221.103:10035",
"78.141.221.103:10036",
"78.141.221.103:10037",
"78.141.221.103:10038",
"78.141.221.103:10039",
"78.141.221.103:10040",
"78.141.221.103:10041",
"78.141.221.103:10042",
"78.141.221.103:10043",
"78.141.221.103:10044",
"78.141.221.103:10045",
"78.141.221.103:10046",
"78.141.221.103:10047",
"78.141.221.103:10048",
"78.141.221.103:10049",
"78.141.221.103:10050"]
```


      File "<ipython-input-4-940da7ae3994>", line 1
        x="78.141.221.103:10001
                               ^
    SyntaxError: EOL while scanning string literal




```python
url='http://free-proxy.cz/en/proxylist/country/PL/all/ping/all'
page = requests.get(url)
doc = lh.fromstring(page.content)

```


    ---------------------------------------------------------------------------

    TimeoutError                              Traceback (most recent call last)

    ~/anaconda3/lib/python3.6/site-packages/urllib3/connection.py in _new_conn(self)
        140             conn = connection.create_connection(
    --> 141                 (self.host, self.port), self.timeout, **extra_kw)
        142 


    ~/anaconda3/lib/python3.6/site-packages/urllib3/util/connection.py in create_connection(address, timeout, source_address, socket_options)
         82     if err is not None:
    ---> 83         raise err
         84 


    ~/anaconda3/lib/python3.6/site-packages/urllib3/util/connection.py in create_connection(address, timeout, source_address, socket_options)
         72                 sock.bind(source_address)
    ---> 73             sock.connect(sa)
         74             return sock


    TimeoutError: [Errno 60] Operation timed out

    
    During handling of the above exception, another exception occurred:


    NewConnectionError                        Traceback (most recent call last)

    ~/anaconda3/lib/python3.6/site-packages/urllib3/connectionpool.py in urlopen(self, method, url, body, headers, retries, redirect, assert_same_host, timeout, pool_timeout, release_conn, chunked, body_pos, **response_kw)
        600                                                   body=body, headers=headers,
    --> 601                                                   chunked=chunked)
        602 


    ~/anaconda3/lib/python3.6/site-packages/urllib3/connectionpool.py in _make_request(self, conn, method, url, timeout, chunked, **httplib_request_kw)
        356         else:
    --> 357             conn.request(method, url, **httplib_request_kw)
        358 


    ~/anaconda3/lib/python3.6/http/client.py in request(self, method, url, body, headers, encode_chunked)
       1238         """Send a complete request to the server."""
    -> 1239         self._send_request(method, url, body, headers, encode_chunked)
       1240 


    ~/anaconda3/lib/python3.6/http/client.py in _send_request(self, method, url, body, headers, encode_chunked)
       1284             body = _encode(body, 'body')
    -> 1285         self.endheaders(body, encode_chunked=encode_chunked)
       1286 


    ~/anaconda3/lib/python3.6/http/client.py in endheaders(self, message_body, encode_chunked)
       1233             raise CannotSendHeader()
    -> 1234         self._send_output(message_body, encode_chunked=encode_chunked)
       1235 


    ~/anaconda3/lib/python3.6/http/client.py in _send_output(self, message_body, encode_chunked)
       1025         del self._buffer[:]
    -> 1026         self.send(msg)
       1027 


    ~/anaconda3/lib/python3.6/http/client.py in send(self, data)
        963             if self.auto_open:
    --> 964                 self.connect()
        965             else:


    ~/anaconda3/lib/python3.6/site-packages/urllib3/connection.py in connect(self)
        165     def connect(self):
    --> 166         conn = self._new_conn()
        167         self._prepare_conn(conn)


    ~/anaconda3/lib/python3.6/site-packages/urllib3/connection.py in _new_conn(self)
        149             raise NewConnectionError(
    --> 150                 self, "Failed to establish a new connection: %s" % e)
        151 


    NewConnectionError: <urllib3.connection.HTTPConnection object at 0x1134f3208>: Failed to establish a new connection: [Errno 60] Operation timed out

    
    During handling of the above exception, another exception occurred:


    MaxRetryError                             Traceback (most recent call last)

    ~/anaconda3/lib/python3.6/site-packages/requests-2.19.1-py3.6.egg/requests/adapters.py in send(self, request, stream, timeout, verify, cert, proxies)
        444                     retries=self.max_retries,
    --> 445                     timeout=timeout
        446                 )


    ~/anaconda3/lib/python3.6/site-packages/urllib3/connectionpool.py in urlopen(self, method, url, body, headers, retries, redirect, assert_same_host, timeout, pool_timeout, release_conn, chunked, body_pos, **response_kw)
        638             retries = retries.increment(method, url, error=e, _pool=self,
    --> 639                                         _stacktrace=sys.exc_info()[2])
        640             retries.sleep()


    ~/anaconda3/lib/python3.6/site-packages/urllib3/util/retry.py in increment(self, method, url, response, error, _pool, _stacktrace)
        387         if new_retry.is_exhausted():
    --> 388             raise MaxRetryError(_pool, url, error or ResponseError(cause))
        389 


    MaxRetryError: HTTPConnectionPool(host='free-proxy.cz', port=80): Max retries exceeded with url: /en/proxylist/country/PL/all/ping/all (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x1134f3208>: Failed to establish a new connection: [Errno 60] Operation timed out',))

    
    During handling of the above exception, another exception occurred:


    ConnectionError                           Traceback (most recent call last)

    <ipython-input-3-2bd09a875196> in <module>()
          1 url='http://free-proxy.cz/en/proxylist/country/PL/all/ping/all'
    ----> 2 page = requests.get(url)
          3 doc = lh.fromstring(page.content)


    ~/anaconda3/lib/python3.6/site-packages/requests-2.19.1-py3.6.egg/requests/api.py in get(url, params, **kwargs)
         70 
         71     kwargs.setdefault('allow_redirects', True)
    ---> 72     return request('get', url, params=params, **kwargs)
         73 
         74 


    ~/anaconda3/lib/python3.6/site-packages/requests-2.19.1-py3.6.egg/requests/api.py in request(method, url, **kwargs)
         56     # cases, and look like a memory leak in others.
         57     with sessions.Session() as session:
    ---> 58         return session.request(method=method, url=url, **kwargs)
         59 
         60 


    ~/anaconda3/lib/python3.6/site-packages/requests-2.19.1-py3.6.egg/requests/sessions.py in request(self, method, url, params, data, headers, cookies, files, auth, timeout, allow_redirects, proxies, hooks, stream, verify, cert, json)
        510         }
        511         send_kwargs.update(settings)
    --> 512         resp = self.send(prep, **send_kwargs)
        513 
        514         return resp


    ~/anaconda3/lib/python3.6/site-packages/requests-2.19.1-py3.6.egg/requests/sessions.py in send(self, request, **kwargs)
        620 
        621         # Send the request
    --> 622         r = adapter.send(request, **kwargs)
        623 
        624         # Total elapsed time of the request (approximately)


    ~/anaconda3/lib/python3.6/site-packages/requests-2.19.1-py3.6.egg/requests/adapters.py in send(self, request, stream, timeout, verify, cert, proxies)
        511                 raise SSLError(e, request=request)
        512 
    --> 513             raise ConnectionError(e, request=request)
        514 
        515         except ClosedPoolError as e:


    ConnectionError: HTTPConnectionPool(host='free-proxy.cz', port=80): Max retries exceeded with url: /en/proxylist/country/PL/all/ping/all (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x1134f3208>: Failed to establish a new connection: [Errno 60] Operation timed out',))



```python
tr_elements = doc.xpath('//*[@id="proxy_list"]')
```


```python
#Create empty list
col=[]
i=0
#For each row, store each first element (header) and an empty list
for t in tr_elements[0]:
    i+=1
    name=t.text_content()
    col.append((name,[]))
```


```python
#https://free-proxy-list.net

import requests
import lxml.html as lh
import pandas as pd

url='https://free-proxy-list.net'
page = requests.get(url)
doc = lh.fromstring(page.content)
tr_elements = doc.xpath('//tr')


#Create empty list
col=[]
i=0
#For each row, store each first element (header) and an empty list
for t in tr_elements[0]:
    i+=1
    name=t.text_content()
    col.append((name,[]))

for j in range(1,len(tr_elements)):
    T=tr_elements[j]
    #If row is not of size 10, the //tr data is not from our table 
    if len(T)!=8:
        break
    #i is the index of our column
    i=0
    #Iterate through each element of the row
    for t in T.iterchildren():
        data=t.text_content() 
        #Check if row is empty
        if i>0:
        #Convert any numerical value to integers
            try:
                data=int(data)
            except:
                pass
        #Append the data to the empty list of the i'th column
        col[i][1].append(data)
        #Increment i for the next column
        i+=1
        
Dict={title:column for (title,column) in col}
df=pd.DataFrame(Dict)

ROTATING_PROXY_LIST = []
for i in df.itertuples():
    ROTATING_PROXY_LIST += [":".join([str(i._1),str(i.Port)])]

HTTPS_PROXIES = []
for i in df.query("Https == 'yes'").itertuples():
    HTTPS_PROXIES += [":".join(["https","//"+str(i._1),str(i.Port)])]
    
HTTP_PROXIES = []
for i in df.query("Https == 'no'").itertuples():
    HTTP_PROXIES += [":".join(["http","//"+str(i._1),str(i.Port)])]
```


```python
ROTATING_PROXY_LIST
```


```python
ROTATING_PROXY_LIST = [
    'proxy1.com:8000',
    'proxy2.com:8031',
    # ...
]
```


```python
import random
random.shuffle(ROTATING_PROXY_LIST)
```


```python
ROTATING_PROXY_LIST
```
