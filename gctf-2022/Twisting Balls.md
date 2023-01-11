# Twisting Balls

Challenge image:  
<img src="https://user-images.githubusercontent.com/58442255/210239770-fcc878f2-57c0-4c55-881c-5e51b0271c05.png" width="400"/>

We are given a netcat connection address and port to connect to, and the challenge name is called "Twisting Balls". This seems like a Mersenne Twister guessing game, as the name implies ("Twisting")  
Upon connection, we see:  
![image](https://user-images.githubusercontent.com/58442255/210241239-4023aa26-9088-49b7-872c-0bc034c84861.png)

## Solving the challenge
We get a hint that its a 32 bit number, and we can guess this with a Mersenne Twister Predictor.
We need to guess the number 50 times.

The output is quite structured, after the initial text
```
Twister balls! get yer twister balls!
But only if you can beat my balls to it!
Guess the next number 50 times!
Hint: its a 32 bit number

```
there is a prompt `>>>`, in which if you type any number (even a correct number), it will output `The Twister Balls Guesses: {number here}`.  

The program EOFs after a period of timeout, and a restart of the connection/program is required. Hence, each guess should not take very long.  
It is impossible to do this manually.

- A brief intro  
Random numbers on most systems, if not cryptographically secure, are generated mostly with the Mersenne Twister algorithm: https://en.wikipedia.org/wiki/Mersenne_Twister, specifically MT19337, which has a 32 bit word length (matches the challenge prompt), based on the Mersenne Prime of 2<sup>19337</sup> - 1.  
This allows anyone to predict the next value, given the previous 624 values. (refer to the last point of https://en.wikipedia.org/wiki/Mersenne_Twister#Disadvantages)

I used `pwntools` (`pwn`), a Python library used for pwn attacks and similar CTF challenges. It has useful utilities such as connecting to remote, interactive mode, and sending output from the program with a simple API.
I also used this library: https://github.com/kmyk/mersenne-twister-predictor for guessing the values. Although the repo is archived, the package is still available on PyPI and works well, and installation is minimal.

My code is below, I shall explain it step-by-step.
```python
from pwn import *
import time
from mt19937predictor import MT19937Predictor
predictor = MT19937Predictor()
conn = remote('chall2.gctf.dismgryphons.com', 28165)


for i in range(5):
    print(conn.recvline())

for i in range(624):
    conn.send(b"\n")
    a = conn.recvline().decode("utf-8")

    if a.strip() == ">>>":
        # Check to mess up pwn code.
        # We need to pause execution.
        conn.interactive()
        
        guess = int(input("whats the displayed seq?"))
        predictor.setrandbits(int(guess), 32)
        continue
    
    
    
    guess = str(a).strip(">>> The Twister Balls Guesses: ").strip()
    print(f"Guess is {guess}")
    predictor.setrandbits(int(guess), 32)
    conn.recvline()
    
pred = []
for i in range(60):
    pred.append(str(predictor.getrandbits(32)))

with open("prediction.txt", "w") as f:
    f.write("\n".join([str(x) for x in pred]))

for i in range(49):
    guess = pred[i]
    print(f"I'm guessing {guess}")
    conn.send((guess + "\n").encode("utf-8"))
    
    print(conn.recvline())
    conn.recvline()
    
guess = pred[49]
print(f"I'm guessing {guess}")
conn.send((guess + "\n").encode("utf-8"))
conn.interactive() # Interactive mode to show the flag, we do not need to mess with conn.recvline anymore
```

Firstly, the code imports required libraries, initialises variables and connects to the remote URL via pwntools. (`conn = remote('chall2.gctf.dismgryphons.com', 28165)`)  
It then reads the first 5 lines (which is the initial text mentioned earlier), printing it to console (we are not using it)


Afterwards, it begins guessing (624 times in the for loop)
After a newline is sent, an output will be returned (Sample: `>>> The Twister Balls Guesses: 1307351396`). This program strips the output line of the string, only getting the number.  
It then feeds this into the predictor (`predictor.setrandbits(int(guess), 32)`), and receives an empty line before moving to the next loop iteration.

The code in the middle:
```python
    if a.strip() == ">>>":
        # Check to mess up pwn code.
        # We need to pause execution.
        conn.interactive()
        
        guess = int(input("whats the displayed seq?"))
        predictor.setrandbits(int(guess), 32)
        continue
```
is for answering the check given after 200 attempts at guessing. (The "Balls Check")
![image](https://user-images.githubusercontent.com/58442255/210246684-fe7fa61d-e188-412b-ae0c-e32512c5def4.png)

I used manual input for it, as parsing was too tedious and my code failed on the 2nd check, hindering progress.
After completing the check, press Ctrl+C to exit interactive mode. Since the output will be printed in interactive mode and unavailable in the program, I added an `input` statement to feed this value to the predictor so it gets the right state.

After 3 checks, and 624 iterations, the loop will exit, and the predictor will have the internal state of the Mersenne Twister.

It then gets the next 60 values, saves them to a list, then a file for logging purposes. This is for debugging purposes/so I can test it manually as well.
```python
pred = []
for i in range(60):
    pred.append(str(predictor.getrandbits(32)))

with open("prediction.txt", "w") as f:
    f.write("\n".join([str(x) for x in pred]))
```


I then submit the first 50 guesses into the connection (with some debug statements and recvline to skip blank lines), and the flag is obtained!
```python
for i in range(49):
    guess = pred[i]
    print(f"I'm guessing {guess}")
    conn.send((guess + "\n").encode("utf-8"))
    
    print(conn.recvline())
    conn.recvline()
    
guess = pred[49]
print(f"I'm guessing {guess}")
conn.send((guess + "\n").encode("utf-8"))
conn.interactive() # Interactive mode to show the flag, we do not need to mess with conn.recvline anymore
```
![Screenshot](https://user-images.githubusercontent.com/58442255/210247385-d22cab06-70df-4db1-acc8-9bf639a21da3.png)

```
GCTF{tW1s7iNg_bA11_bA$h3r}
```


Thanks for reading my write-up. For feedback, please open an issue on this repo.
