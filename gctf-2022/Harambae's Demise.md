# Harambae's demise 

Here is the challenge for GCTF 2022 -  Harambae's demise.


<img src="https://user-images.githubusercontent.com/58442255/210307656-98a3014b-7e7b-4250-aa1f-fc491a5b3fa3.png" width=300/>

The file attached is available [here](https://github.com/czlucius/ctf-writeups/blob/main/gctf-2022/harambae_capture.pcapng). 

## Solving the challenge
1. Upon opening the challenge pcap file, we see this:  

![image](https://user-images.githubusercontent.com/58442255/210307979-fa047646-5c02-43cb-8adc-dad3ba69cf65.png)
2. After scrolling through the entries, we see these:
Some of it are not that important, but I have selected some to show here.

![image](https://user-images.githubusercontent.com/58442255/210308953-8e563fa7-a231-4d06-9881-5c5926e91f98.png)
![image](https://user-images.githubusercontent.com/58442255/210308964-18a3a82c-9426-41f1-8dd2-009ffd7bea13.png)
![image](https://user-images.githubusercontent.com/58442255/210308975-44cdce50-92a8-4cd5-9947-26ee42ef3788.png)
![image](https://user-images.githubusercontent.com/58442255/210308985-c9c4ea95-a093-4834-a810-01588a7fc83c.png)

We then see some log in prompts, such as this:    
![image](https://user-images.githubusercontent.com/58442255/210309006-28d4f256-314c-4f50-a665-29ba874b965e.png)


Apparently the password was forgotten and a reset was performed.

![image](https://user-images.githubusercontent.com/58442255/210309221-ce236b73-1c3a-4c75-90bb-11a4b7601146.png)
![image](https://user-images.githubusercontent.com/58442255/210309274-0cb07477-d611-429b-a527-b5eed718a445.png)

The password was leaked in one of the login prompts, and we can see that it is `garAMba3_gAnG_11`.

![image](https://user-images.githubusercontent.com/58442255/210309334-19a68219-47f5-4f27-a778-a02d3ccaea58.png)

We also get a file (.png extension) in the FTP-DATA exported object list.

![image](https://user-images.githubusercontent.com/58442255/210309507-536202f4-4d00-44fd-a604-49f668f6f575.png)

Exporting it and decrypting it with the password yields a PNG file which we can open:  

![image](https://user-images.githubusercontent.com/58442255/210309706-d9197e4c-bf40-4bfa-9981-d0ee002d2c5d.png)


And we have the flag!

![image](https://user-images.githubusercontent.com/58442255/210309841-f7a74634-d22f-4640-99dc-314bb0609fa6.png)

