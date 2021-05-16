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

# Ethereum JSON RPC usage example

```python
import pandas as pd

%load_ext restmagic

pd.set_option('display.max_colwidth', -1)
```

```python
# Helpers
hex_num = lambda v: int(v, 16)
wei_to_gwei = lambda v: v / 10 ** 9
wei_to_ether = lambda v: v / 10 ** 18
```

## Get latest block

```python
%%rest -q
POST  https://mainnet.infura.io/
Content-Type: application/json
    
{
    "jsonrpc": "2.0",
    "method": "eth_getBlockByNumber",
    "params": ["latest", true],
    "id": 1
}
```

```python
r = _
result = r.json()['result']
print("Latest block number: {}".format(hex_num(result['number'])))
transactions = result['transactions']
```

```python
df = pd.DataFrame(transactions, columns=['hash', 'gas', 'gasPrice', 'value'])
df['Gas limit'] = df['gas'].apply(hex_num)
df['Gas price, Gwei'] = df['gasPrice'].apply(lambda v: wei_to_gwei(hex_num(v)))
df['Value, Ether'] = df['value'].apply(lambda v: wei_to_ether(hex_num(v)))
df = df[['hash', 'Gas limit', 'Gas price, Gwei', 'Value, Ether']]
```

```python
df.hist(figsize=(20, 12))
```

```python
df.describe()
```

```python
df = df[df['Value, Ether'] > 0]
print("Transfers, for {:.2f} Ether in total".format(df['Value, Ether'].sum()))
df
```
