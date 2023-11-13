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

### Quadratic Residues
A quadratic residue is an integer that is congruent to a perfect square modulo a given modulus $p$
```python
p = ...
ints = [..., ..., ..., ...] # list of ints for which we have to check if their squares are in the Z_p field

ans = [x for x in range(p) if(pow(x, 2, p) in ints)]
```

### Lengendre Symbol
The Legendre symbol is denoted as $(\frac{a}{p})$, and it expresses the solvability of the quadratic congruence $x^2 \equiv a \mod{x}$
$$\begin{cases}(\frac{a}{p}) = 1 \text{ if } \exists x \text{ | } x^2 \mod{p} \\ (\frac{a}{p}) = -1 \text{ if } \nexists x \text{ | } x^2 \mod{p} \\ (\frac{a}{p}) = 0 \text{ if } a \equiv 0 \mod{p}\end{cases}$$
```python
# (a / p) = 1 if a is a quadratic residue and a ≢ 0 mod p
# (a / p) = -1 if a is a quadratic non-residue mod p
# (a / p) = 0 if a ≡ 0 mod p
p = ...
ints = [..., ..., ..., ...]

quad = [x for x in ints if(pow(x, (p - 1)//2, p) == 1)]

res = quad[0]
print(pow(res, (p + 1)//4, p))
```

---

### Tonelli-Shanks Algorithm for Modular Square Roots
The Tonelli-Shanks algorithm calculates $r$ in where $r^2 = a \mod{p}$, the algorithm doesn't work for non-prime moduli.
```python
def legendre(a, p):
    return pow(a, (p - 1) // 2, p)

def tonelli(n, p):
    assert legendre(n, p) == 1, "not a square (mod p)"
    q = p - 1
    s = 0

    while q % 2 == 0:
        q //= 2
        s += 1
    if s == 1:
        return pow(n, (p + 1) // 4, p)
    for z in range(2, p):
        if p - 1 == legendre(z, p):
            break

    c = pow(z, q, p)
    r = pow(n, (q + 1) // 2, p)
    t = pow(n, q, p)
    m = s
    t2 = 0

    while (t - 1) % p != 0:
        t2 = (t * t) % p

        for i in range(1, m):
            if (t2 - 1) % p == 0:
                break
			t2 = (t2 * t2) % p

        b = pow(c, 1 << (m - i - 1), p)
        r = (r * b) % p
        c = (b * b) % p
        t = (t * c) % p
        m = i
    return r

a = ...
p = ...

root = tonelli(a, p)
```

---

### Chinese Reminder Theorem
The Chinese Remainder Theorem gives a unique solution to a set of linear congruences if their moduli are coprime. Given $a_i$ and $n_i$ such that
$$\begin{cases}x \equiv a_1 \mod{n_1}\\x \equiv a_2 \mod{n_2}\\\cdots\\x \equiv a_n \mod{n_n}\end{cases}$$
there is a unique solution $x \equiv a \mod{N}$ where $N = n_1 \cdot n_2 \cdot \cdots \cdot n_n$.
```python
from Crypto.Util.number import inverse

def chineseReminderTheorem(a, m):
    Mul = 1
    for i in m:
        Mul *= i
    M = [Mul // x for x in m]
    y = [inverse(M[i], m[i]) for i in range(len(m))]
    ans = 0
    for i in range(len(m)):
        ans += a[i] * M[i] * y[i]
    return ans % Mul

a = ...
m = ...
print(chineseReminderTheorem(a, m))
```

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
To find primes given a modulus you can use [factordb](http://factordb.com) or try to factorize them yourself.
FactorDB also has a python implementation
```python
from factordb.factordb import FactorDB

N = ...
f = FactorDB(N)
```

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
