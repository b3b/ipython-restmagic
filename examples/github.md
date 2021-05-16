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

# GitHub API usage example

```python
import pandas as pd
%load_ext restmagic
```

Some calls require personal API token: https://blog.github.com/2013-05-16-personal-api-tokens/

```python
token = ''
```

```python
%%rest_root https://api.github.com
Accept: application/vnd.github.v3+json
Authorization: Token $token
```

## Get top 10 forked projects from the GitHub, for the "ipython" query

```python
r = %rest -q search/repositories?q=ipython&sort=forks&per_page=10
df = pd.DataFrame(r.json()['items'], columns=('full_name', 'forks_count', 'watchers'))
df.set_index('full_name', inplace=True)
df
```

```python
df.plot(kind='barh')
```

<!-- #region hideCode=true -->
## Follow Github User
Personal API token is required to perform the call: https://blog.github.com/2013-05-16-personal-api-tokens/
<!-- #endregion -->

```python
%rest PUT user/following/gvanrossum
```

### Unfollow GitHub user

```python
%rest -q DELETE user/following/gvanrossum
```

<!-- #region hideCode=true -->
## Search GitHub for "pritn" string in Python code
<!-- #endregion -->

```python
r = %rest -q search/code?q=pritn+in:file+language:python
data = r.json()
urls = [i['html_url'] for i in data['items']]
print('\n'.join(urls))
print("== {0} of total {1} ==".format(len(urls), data['total_count']))
```
