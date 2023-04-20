
# Insecure Keyed Hash 

- Category: Crypto
- Difficulty: Easy

Challenge text:
```
I have created a new keyed-hash algorithm! It's faster and better than HMAC! I'll be famous!
```

Challenge files: [insecure-keyed-hash-server.py](insecure-keyed-hash-server.py) (zipped)  
Challenge server: ` nc nc.lagncra.sh 8012 ` (netcat)
## Solving the challenge

From the code, we can see that this is an authentication algorithm, used to sign and verify messages.  
It appears that the code outputs the flag when we give a signed version of "Better than HMAC!", but when we try to enter "Better than HMAC!", we get "Indeed! Our new algorithm runs much faster than HMAC :)" instead.

How then shall we sign the string?  
We can see that the key is generated here:
```python
key = "".join(choices(ascii_lowercase, k=5))
```
The key is composed of 5 ASCII lowercase characters. This is a weak key and would be trivial to brute-force.

Using a script, we can brute force the password. Firstly, we sign a random piece of text, then try to match all possible signatures until we find a match.
```python
from string import ascii_lowercase
from random import choices
from hashlib import md5
from itertools import permutations
import sys
msg, enc = input().split(".")

for combi in permutations(ascii_lowercase,5):
	key = "".join(combi)
  digest = md5((key + msg).encode()).hexdigest()
  print(f"plaintext is {key} digest is {digest}")
  if digest == enc:
      print("We found the key!")
      print(key)
      sys.exit()

```
Let's sign a message.
`message.cb02ee67a3353d4c9d1fa09bb4e91afe`

Using the brute force script, we get the key `zxcls` (different each time!!)  
We then proceed to generate the signature:
```python
from string import ascii_lowercase
from random import choices
from hashlib import md5
print("Better than HMAC!." + md5(("zxcls" + "Better than HMAC!").encode()).hexdigest())
```

We get the signed message: `Better than HMAC!.5e513eb625df5af8413c0703652fe5b9`

Feeding this into the validation function, we get the flag.
```
Enter option: 2
Enter signed message: Better than HMAC!.5e513eb625df5af8413c0703652fe5b9
Message verified!
LNC2023{H0w?_1t_5hoU1d_h4v3_be3n_5tr0ng3r_7h4N_HMAC_QAQ!}
```

Flag: `LNC2023{H0w?_1t_5hoU1d_h4v3_be3n_5tr0ng3r_7h4N_HMAC_QAQ!}`
