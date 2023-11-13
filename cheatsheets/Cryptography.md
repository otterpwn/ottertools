# Cryptography Cheatsheet
## Setup
[Install Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)
[Install Mamba](https://ask.sagemath.org/question/51555/ubuntu-1804-apt-install-modulenotfounderror-no-module-named-sage/)
[Install SageMath with Mamba](https://ask.sagemath.org/question/51555/ubuntu-1804-apt-install-modulenotfounderror-no-module-named-sage/)

---

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

---

## Mathematics
### GCD - Greatest Common Divisor
```python
from Crypto.Util.number import GCD

a = x
b = y
GCD(a, b)
```

### EGCD - Extended Greatest Common Divisor
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

### Modular Arithmetic (extreme summary)
$$a \equiv b \mod{m}$$
If $m$ divides $a$ then $a \equiv 0 \mod{m}$
Generally $b = a \mod{n}$

---

## Data / Key Formats
### PEM RSA Key
```python
from Crypto.PublicKey import RSA

with open("key.pem") as f:
    data = f.read()

key = RSA.importKey(data)
n = key.n
e = key.e
...
```

### DER RSA Certificate
```python
from OpenSSL.crypto import load_certificate, FILETYPE_ASN1

with open("cert.der", "rb") as f:
    data = f.read()
    cert = load_certificate(FILETYPE_ASN1, data)

key = cert.to_cryptography().public_key()
n = key.public_numbers().n
...
```

### RSA Keys
```python
from Crypto.PublicKey import RSA

with open("id_rsa.pub") as f:
    data = f.read()

key = RSA.importKey(data)
n = key.n
...
```

---

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

### Primes Attacks
- $N$ is a big prime
```python
from Crypto.Util.number import inverse, long_to_bytes

n = ...
e = ...
ct = ...

d = inverse(e, n - 1)
pt = pow(ct, d, n)

print(long_to_bytes(pt).decode())
```

- $N = q \cdot q$ (the same prime is squared)
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

- More than two primes are used
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

- **Fermat Factorization**: the difference between $p$ and $q$ is small
```python
from Crypto.Util.number import long_to_bytes, inverse

def fermatFactorization(N):
    a = ceil(sqrt(N))
    b = a ** 2 - N

    while not b.is_square():
        a += 1
        b = a ** 2 - N

    return a - sqrt(b)

n = ...
e = ...
c = ...

p = fermatFactorization(n)
q = n // p
phi = (p - 1) * (q - 1)
d = inverse(e, phi)
pt = pow(c, d, n)
```

### Public / Private Exponent Attacks
- $e$ is really small
```python
from Crypto.Util.number import long_to_bytes

n = ...
e = 1 # small value
ct = ...

if ct < n:
    print(long_to_bytes(ct).decode())
```

- $n \gt\gt ct$
```python
from Crypto.Util.number import long_to_bytes
from gmpy2 import iroot

n = ... # n >> ct
e = ...
ct = ...

print(long_to_bytes(iroot(ct, e)[0]).decode())
```

- **Wiener's attack**: $d \lt \frac{1}{3}\sqrt[4]{n}$ given $e$ and $n$
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

- **Boneh-Durfee attack**: $d \lt N^{0.292}$
```
https://raw.githubusercontent.com/mimoo/RSA-and-LLL-attacks/master/boneh_durfee.sage
```
Plug the values for $N$, $e$ and $ct$ in the `example` function at the end of the script, to decode the ciphertext you can add the following at the end
```python
if d:
	pt = long_to_bytes(pow(c, d, N)).decode()
	print(pt)
```
