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

# Django login form

```python
from bs4 import BeautifulSoup

%load_ext restmagic
%rest_root http://mezzanine.jupo.org
```

## First attempt to login

```python
%%rest
POST /en/admin/login/?next=/en/admin/
Content-Type: application/x-www-form-urlencoded

username=demo&password=demo
```

### Enable cookies

```python
%rest_session
```

<!-- #region hideCode=true -->
### Get the login page, this will set session CSRF cookie
<!-- #endregion -->

```python
r = %rest -q /en/admin/login/
```

<!-- #region hideCode=true -->
### Still can't login, need a CSRF token
<!-- #endregion -->

```python
%%rest
POST /en/admin/login/?next=/en/admin/
Content-Type: application/x-www-form-urlencoded

username=demo&password=demo
```

### CSRF token can be obtained from the cookie

```python
token = r.cookies['csrftoken']
token
```

### Login success

```python
%%rest -q
POST /en/admin/login/?next=/en/admin
Content-Type: application/x-www-form-urlencoded

username=demo&password=demo&csrfmiddlewaretoken=$token
```

### CSRF token from the HTML form is also works

```python
%rest_session
r = %rest -q /en/admin/login/
soup = BeautifulSoup(r.text)
token = soup.find('input', {'name': 'csrfmiddlewaretoken'}).get('value')
print("Token from the hidden form field: " + token)
```

```python
%%rest -q
POST /en/admin/login/?next=/en/admin
Content-Type: application/x-www-form-urlencoded

username=demo&password=demo&csrfmiddlewaretoken=$token
```
