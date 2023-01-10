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