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

# Sending SMS with HiLink API

HiLink API is available for some of 3G/LTE modems and routers.

This is example of how it was used on a particular modem, for other devices it will work differently.

**Some of the error API endpoints returns:**
* 100002 -- SYSTEM NO SUPPORT
* 100003 -- SYSTEM NO RIGHTS
* 100004 -- SYSTEM BUSY
* 108001 -- LOGIN USERNAME WRONG
* 108002 -- LOGIN PASSWORD WRONG
* 108003 -- LOGIN ALREADY LOGIN
* 108006 -- LOGIN USERNAME PWD WRONG
* 108007 -- LOGIN USERNAME PWD ORERRUN
* 120001 -- VOICE BUSY
* 125001 -- WRONG TOKEN
* 125002 -- WRONG SESSION
* 125003 -- WRONG SESSION TOKEN


```python
import re
%load_ext restmagic
```

Set device address:

```python
%rest_root http://192.168.8.1
```

Start the session. SessionID cookie is required to use device functions:

```python
%rest_session
%rest -q /
```

Get the config:

```python
r = %rest -q /config/global/config.xml
re.findall(r'^.*login.*$', r.text, re.MULTILINE)
```

`login == 1` means that login is required to use device functions.
Auth token is required to login, let's get that token first:

```python
r = %rest -v /api/webserver/SesTokInfo
token = re.search('<TokInfo>(.*)</TokInfo>', r.text).group(1) 
print("Token is: " + token)
```

Login state check:

```python
%rest -v /api/user/state-login
```

`password_type` == 4 means password should be encoded in a weird way

```python
import hashlib
from base64 import b64encode
from binascii import hexlify


def sha256(data):
    return hexlify(hashlib.sha256(data).digest())


def encode_password(name, raw_password, token):
    return b64encode(sha256(
        name + b64encode(sha256(raw_password)) + token
    ))


username = 'admin'
raw_password = 'admin'
password = encode_password(username, raw_password, token)
password
```

SessionID is stored in cookie, Token in`__RequestVerificationToken` header, login and password in form fields.

Ready to login:

```python
%%rest -v POST /api/user/login
__RequestVerificationToken: $token

<?xml version: "1.0" encoding="UTF-8"?>
    <request>
        <Username>${username}</Username>
        <Password>${password}</Password>
        <password_type>4</password_type>
    </request>
```

```python
r = _
```

Login endpoint returns a a bunch of tokens to use:

```python
r.headers['__RequestVerificationToken']
```

Each API call require a new token:

```python
tokens = (t for t in filter(None, r.headers['__RequestVerificationToken'].split('#')))
token = tokens.next()
print("Next token is: " + token)
```

```python
friend_phone = ''  # random phone number here 
```

```python
%%rest POST /api/sms/send-sms
__RequestVerificationToken: $token
    
<?xml version='1.0' encoding='UTF-8'?>
    <request>
        <Index>-1</Index>
        <Phones><Phone>${friend_phone}</Phone></Phones>
        <Sca></Sca>
        <Content>Hello? Is there anybody in there?</Content>
        <Length>-1</Length>
        <Reserved>1</Reserved>
        <Date>-1</Date>
    </request>
```

SMS was sended, let's try to send more

```python
%%rest POST /api/sms/send-sms
__RequestVerificationToken: $token
    
<?xml version='1.0' encoding='UTF-8'?>
    <request>
        <Index>-1</Index>
        <Phones><Phone>${friend_phone}</Phone></Phones>
        <Sca></Sca>
        <Content>Just nod if you can hear me.</Content>
        <Length>-1</Length>
        <Reserved>1</Reserved>
        <Date>-1</Date>
    </request>
```

 `125003` error returned - SMS is not sended, need to use the next token:

```python
token = tokens.next()
print("Next token is: " + token)
```

```python
%%rest POST /api/sms/send-sms
__RequestVerificationToken: $token
    
<?xml version='1.0' encoding='UTF-8'?>
    <request>
        <Index>-1</Index>
        <Phones><Phone>${friend_phone}</Phone></Phones>
        <Sca></Sca>
        <Content>Is there anyone at home?</Content>
        <Length>-1</Length>
        <Reserved>1</Reserved>
        <Date>-1</Date>
    </request>
```
