# Cryptography Cheatsheet
## Encoding
- Ascii Encoding
```python
data = [99, 114, ..., 125]

message = ""
for number in data:
    message += chr(number)
```

- Hex Encoding
```python
data = "637279707...f776f72"
message = bytes.fromhex(data)
```

- Base64 Encoding
```python
import base64

data = "..."
message = base64.b64decode(data)
```

- Long to Bytes
```python
from Crypto.Util.number import long_to_bytes

data = 11515195...6269
message = long_to_bytes(data)
```

## Mathematics
- Greatest Common Divisor (GCD)
```python
from Crypto.Util.number import GCD

a = x
b = y
GCD(a, b)
```

- Extended Greatest Common Divisor (EGCD)
```python
from Crypto.Util.number import GCD

x = ...
y = ...

if x < y:
    x, y = y, x

a, b = x, y
u1, u2 = 1, 0
v1, v2 = 0, 1

while b > 0:
    q, r = divmod(a, b)
    a, b = b, r

    u1, u2 = u2, u1 - q * u2
    v1, v2 = v2, v1 - q * v2

# results are u1 and v1
```

- Modular Arithmetic
$$a \equiv b \mod{m}$$
If $m$ divides $a$ then $a \equiv 0 \mod{m}$
Generally $b = a \mod{n}$

## Data / Key Formats
- Import PEM RSA Key
```python
from Crypto.PublicKey import RSA

with open("key.pem") as f:
    data = f.read()

key = RSA.importKey(data)
n = key.n
e = key.e
...
```

- Import DER RSA Certificate
```python
from OpenSSL.crypto import load_certificate, FILETYPE_ASN1

with open("cert.der", "rb") as f:
    data = f.read()
    cert = load_certificate(FILETYPE_ASN1, data)

key = cert.to_cryptography().public_key()
n = key.public_numbers().n
...
```

- Import RSA Keys
```python
from Crypto.PublicKey import RSA

with open("id_rsa.pub") as f:
    data = f.read()

key = RSA.importKey(data)
n = key.n
...
```

## RSA
```python
from Crypto.Util.number import long_to_bytes, inverse
from sympy import factorint

n = ...
e = ...
c = ...

factors = factorint(n)
p = list(factors.keys())[0]
p = list(factors.keys())[1]

phi = (p - 1) * (q - 1)
d = inverse(e, phi)
pt = long_to_bytes(pow(c, d, n).decode())
```
Or visit [factordb](http://factordb.com).

- If $N$ is a big prime
```python
from Crypto.Util.number import inverse, long_to_bytes

n = ...
e = ...
ct = ...

d = inverse(e, n - 1)
pt = pow(ct, d, n)

print(long_to_bytes(pt).decode())
```

- If $N = q \cdot q$ (the same prime is squared)
```python
from Crypto.Util.number import inverse, long_to_bytes

n = ...
e = ...
ct = ...

phi = n * (n - 1)
d = inverse(e, phi)
pt = pow(ct, d, n)
print(long_to_bytes(pt).decode())
```

- If more than two primes are used
```python
from Crypto.Util.number import inverse, long_to_bytes

n = ...
e = ...
ct = ...
phi = 1
primes = [..., ..., ...]

for p in primes:
    phi *= (p - 1)

d = inverse(e, phi)
pt = pow(ct, d, n)

print(long_to_bytes(pt).decode())
```

- If `e` is really small
```python
from Crypto.Util.number import long_to_bytes

n = ...
e = 1 # small value
ct = ...

if ct < n:
    print(long_to_bytes(ct).decode())
```

- If $n \gt\gt ct$
```python
from Crypto.Util.number import long_to_bytes
from gmpy2 import iroot

n = ... # n >> ct
e = 3
ct = ...

print(long_to_bytes(iroot(ct, e)[0]).decode())
```

- If $e$ has the same bit size of $N$ -> Wiener's attack
```
curl -O https://raw.githubusercontent.com/orisano/owiener/master/owiener.py
```
```python
from Crypto.Util.number import long_to_bytes
import owiener

n = ...
e = ...
c = ...

d = owiener.attack(e, n)
pt = pow(c, d, n)
print(long_to_bytes(pt).decode())
```
