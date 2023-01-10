# Sup3r XOR

> An encrypted .png file was intercepted, crack the encryption and get the flag.  
> Attached files:  
> [chall.py](https://github.com/czlucius/ctf-writeups/blob/main/gctf-2022/chall.py)  
> [enc](https://github.com/czlucius/ctf-writeups/blob/main/gctf-2022/enc)

The title of this challenge suggests XOR encryption.
**Note: I did not solve this challenge during the CTF, but I was very close to doing so, and figured out how to solve it after the CTF.**
## Solving the challenge
Looking at the script,
```python
import hashlib

file = open("image.png",'rb').read()

def MD5(byteval:bytes):
    return hashlib.md5(byteval).digest()

def kdf(key:bytes,length:int):
    blocks = [MD5(key)]
    for i in range(length):
        blocks.append(MD5(blocks[i]))
    print(blocks[0])
    return blocks

def enc(key:bytes,plaintext:bytes):
    blockLength = (len(plaintext) // 16)
    paddingLength = 16 - len(plaintext) % 16
    plaintext += b"\x00"*(paddingLength-1) + paddingLength.to_bytes(1,'big')
    plaintext = [plaintext[i:i+16] for i in range(0, len(plaintext), 16)]
    blocks = kdf(key,blockLength)
    ciphertext = ""

    for i in range(len(blocks)):
        for j in range(len(blocks[i])):
            ciphertext += format(blocks[i][j] ^ plaintext[i][j],"x").zfill(2)

    return ciphertext
enc(b'',file)
```
we see that the plaintext is encrypted in blocks of 16, and blocks of 16 are generated from the MD5 of the initial key supplied using the Key Derivation Function (KDF). It also appears that the password is redacted.  
From `enc`, since XOR encryption does not change the length of the text (apart from the padding which can be removed after decoding), we can retrieve the block length.

The `enc` is encoded in HEX, let's convert the HEX to a raw binary file to process it.  
![image](https://user-images.githubusercontent.com/58442255/211484066-527123c9-6f83-4e6b-ad3a-6a2282d218a4.png)

The `enc`(raw) has a length of 10336, hence a block length of 10336/16-1 = 645.

Here's my decryption script:  
```python
import hashlib
import struct


def MD5(byteval:bytes):
    return hashlib.md5(byteval).digest()


# kdf1b: KDF for 1st block
def kdf1b(first,length:int):
    blocks = [first]
    for i in range(length):
        blocks.append(MD5(blocks[i]))
    return blocks



def dec(initialBlock, ct):
    blockLength = 645
    blocks = kdf1b(initialBlock, blockLength)
    
    new = ct
    new1 = [new[i:i+16] for i in range(0, len(new), 16)] 

        
    pt = b""
    for i in range(len(blocks)):
        for j in range(len(blocks[i])):
            everyiter = blocks[i][j] ^ new1[i][j]
            pt += struct.pack('B', everyiter)
    return pt



ct = open("enc", "rb").read()
initial16 = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A\x00\x00\x00\x0D\x49\x48\x44\x52"
enc16 = ct[:16]
initialBlock = b''
for i in range(16):
    initialBlock += struct.pack('B', initial16[i] ^ enc16[i])



s = dec(initialBlock, ct)
with open("dec.png", "wb") as f:
    f.write(s)
```
We xor back the key of each block obtained via the KDF to get the plaintext (CT ^ key = PT, PT ^ key = CT)   
Since we don't have the key (it is not an empty string), we can use the PNG header, as outlined in the PNG spec. (this was where I was stuck in the CTF, btw)
Every PNG starts with a signature of 8 bytes, and a IHDR of 8 bytes: (in hex)
```
89 50 4E 47 0D 0A 1A 0A 00 00 00 0D 49 48 44 52
```
Thus, we can use this as the first block of plaintext, and obtain the first block of the key, as shown below:
(PT ^ CT = key) 
```python
initial16 = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A\x00\x00\x00\x0D\x49\x48\x44\x52"
enc16 = ct[:16]
initialBlock = b''
for i in range(16):
    initialBlock += struct.pack('B', initial16[i] ^ enc16[i])
```

We then use a modified KDF to get the subsequent blocks.
```python
# kdf1b: KDF for 1st block
def kdf1b(first,length:int):
    blocks = [first]
    for i in range(length):
        blocks.append(MD5(blocks[i]))![decctf txt (2)](https://user-images.githubusercontent.com/58442255/211486216-f1731b45-ecac-40e9-a2a3-28879a918a1c.png)

    return blocks

```
In doing so, we can decrypt the `enc` file without the key, and get the flag!

![dec.png](https://user-images.githubusercontent.com/58442255/211486276-bea075f7-0773-41e2-ab92-079df97ebb60.png)
