from string import ascii_lowercase
from random import choices
from hashlib import md5


def sign(message, key):
    """ Our new keyed-hash message authentication algorithm! So much more simpler then HMAC! """
    return md5((key + message).encode()).hexdigest()

def verify(signed, key):
    """ Verifies if message is signed by key """
    try:
        message, signature = signed.split(".")
        return sign(message, key) == signature
    except:
        return False


key = "".join(choices(ascii_lowercase, k=5))
PASSPHRASE = "Better than HMAC!"

print(
    "Welcome to our new signing service!\n"
    "Our service is extremely secure, feel free to try and break it >:D"
)

while True:
    print(
        "\nOptions:\n"
        "1. Sign messages\n"
        "2. Verify messages\n"
        "3. Exit\n"
    )

    option = input(f"Enter option: ")

    if option == "1":
        message = input("Enter message: ")
        if message == PASSPHRASE:
            print("Indeed! Our new algorithm runs much faster than HMAC :)")
        elif message:
            signed = f"{message}.{sign(message, key)}"
            print(f"Here's your signed message: {signed}")
        else:
            print("No message to sign ¯\_(ツ)_/¯")

    elif option == "2":
        signed = input("Enter signed message: ")
        if verify(signed, key):
            print("Message verified!")
            try:
                if signed.split(".")[0] == PASSPHRASE:
                    with open("flag.txt") as f:
                        flag = f.read()
                        print(flag)
            except:
                pass
        else:
            print("Message verification failed!")

    elif option == "3":
        print("Thanks for using our service. Goodbye!")
        break

    else:
        print("Please choose an option from 1 to 3!")
