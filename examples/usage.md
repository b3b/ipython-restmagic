---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.7.1
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# %rest usage example


## Load

```python
%load_ext restmagic
```

##  Line magic

Arguments of the command are HTTP method and URL.

```python
result = %rest GET https://httpbin.org/json
```

The comand output is a `Response` object of the `requests` library.

```python
type(result)
```

```python
result.json()['slideshow']['title']
```

## Display options

    --verbose, -v  Dump full HTTP session log.
    --quiet, -q     Do not print HTTP request and response.

```python
%rest -q GET https://httpbin.org/json
```

```python
%rest -v GET https://httpbin.org/json
```

## Short form

Method and scheme could be omitted, `GET` and `https://` will be used in this case.

```python
%rest -q httpbin.org/json
```

## Cell magic
Input of the cell magic mimics the HTTP message format:
* `request line`
* `headers`
* `empty line`
* `message body`

Headers and message body are optional.


```python
%%rest POST https://httpbin.org/post
Content-Type: application/x-www-form-urlencoded

username=Gena&email=crocodile@example.org
```

```python
%%rest -v GET https://httpbin.org/user-agent
User-Agent: Mozilla/51.0.2 (X11; Unix x86_64; rv:29.0) Gecko/20170101 Firefox/51.0.2
```

### As with all commands, ouput(`Response` object) is available in `_` variable.

```python
%%rest -q POST https://httpbin.org/post
Content-Type: multipart/form-data;boundary="myboundary"

--myboundary 
Content-Disposition: form-data; name="x"

value1
--myboundary 
Content-Disposition: form-data; name="y"

value2
--myboundary
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: application/octet-stream

Here is a file content.
--myboundary--
```

```python
print(_.json()['files'])
print(_.json()['form'])
```

## Variables

Template strings `$`-based substitutions are supported.

( https://docs.python.org/3/library/string.html#template-strings )

```python
httpbin='https://httpbin.org'
value = 'TEST'
```

```python
%%rest POST $httpbin/post
Content-Type: application/json
Cookie: a=${value}1;b=${value}2

{
    "array here": [
        "$value",
        "$$ escaped: $$value"
    ]
}
```

One restriction, is that `${}` form could not be used in a first line of a query.

This will work: `%rest -q $httpbin/get`,

but this not: `%rest -q ${httpbin}/get`



## Connection options


### --proxy
    --proxy PROXY         Sets the proxy server to use for HTTP and HTTPS.

```python
%rest --proxy http://example.org:9001 httpbin.org
```

### --max-redirects
    --max-redirects MAX_REDIRECTS
                        Set the maximum number of redirects allowed, 30 by default.

```python
%rest -v --max-redirects 0 https://httpbingo.org/redirect/1
```

### --timeout
    --timeout TIMEOUT     Set the maximum number of seconds to wait for a response, 10 by default.

```python
%rest --timeout 0.1 https://httpbin.org/delay/1
```

### --insecure

    --insecure, -k        Disable SSL certificate verification.

```python
%rest -q https://self-signed.badssl.com/
```

```python
%rest -q --insecure https://self-signed.badssl.com/
```

### --cacert

    --cacert CACERT       Path to a file to use as a SSL certificate to verify the peer.

```python
%rest -q --cacert badssl-server.pem https://self-signed.badssl.com/
```

### --cert and --key : specify a client side SSL certificate

    --cert CERT           Path to a file to use as a client side SSL certificate.
    --key KEY             Path to a file to use as a client side SSL private key.

```python
%rest -q https://client.badssl.com/
```

```python
%rest -q --cert badssl.crt --key badssl.key https://client.badssl.com/
```

## Default values
`%rest_root` allows to set values to be used by all subsequent requests:
default HTTP method, first part of an URL, headers and connection options.

The syntax is same as for `%rest`.

```python
%%rest_root --verbose httpbin.org
Authorization: Bearer abcde
User-Agent: restmagic-test
```

```python
%rest /bearer
```

When called without arguments, `%rest_root` clears default values.

```python
%rest_root
```

```python
%rest_root httpbin.org
```

## Sessions


By default, new session is created for every `%rest` request.

`%rest_session` allows to start a persistent session, to be used by all subsequent requests.

```python
%rest_session
```

```python
%rest -q /cookies/set/test/value
```

```python
%rest -v /cookies
```

`%rest-session` options:
    
    --end, -e  End the current the session, and do not start a new one.

```python
%rest_session -e
```

<!-- #region hideCode=true -->
## Display part of response

    --extract expression, -e expression  Extract parts of a response content with the given
                                         Xpath/JSONPath expression.
<!-- #endregion -->

### JSON
Parts of a JSON response could be selectively extracted using a JSONPath expression ( https://goessner.net/articles/JsonPath/index.html ).

`$` (root object) at the beginning could be omitted.


Display only specific item:

```python
%rest -e slideshow.slides.[1].items.[0] /json
```

Display `title` fields of all objects:

```python
%rest -e ..title /json
```

### XML and HTML
Parts of a XML and HTML responses could be selectively extracted using a Xpath expression.


Text of all "title" elements:

```python
%rest -e //title/text() /xml
```

Number of "item" objects:

```python
%rest -e count(//item) /xml
```

Parsing HTML response:

```python
%rest -e '//ul[@class="list-news"]//h2//a/text()' https://www.djangoproject.com/weblog/
```

### -- parser
    --parser <{json,xml,html}>
                        Set which parser to use to extract parts of a response content.

Parser could be explicitly specified. By default, parser is detected from the `Content-Type` header of the response.



```python
%%rest --parser xml -e "/*[name() = 'svg']//*[name() = 'g']/@*[name() = 'id']" /image
Accept: image/svg+xml
```

##  Pretty display

Beware, `%rest` tries to display response in a most pretty way. Very insecure behavior.

```python
%rest /html
```

```python
%%rest /image
Accept: image/png
```
