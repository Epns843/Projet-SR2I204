import getpass, os, hashlib
from os.path import exists 
import re
from Crypto.Cipher import AES
import qrcode 
from argon2 import PasswordHasher
import totp

master_hash = "$argon2id$v=19$m=65536,t=3,p=4$8CJrekUuCG7jD62OFJC/Wg$x0LFj8AUAEWlzhNSCk7oS7hLJpjtnbeQBjvPv3yM2T4"

logins = dict()

master_passwd = ""

def generate_key(): 
    return os.urandom(24).hex()



def check_login(login):
    output = True
    
    if login in logins.keys():
        print("[!] Login already used")
        output = False
        
    p =  re.compile(r'.*([\W]+).*')
    if p.match(login) != None:
        if p.match(login).group()[1] == "'": 
            print(f'[!] Login can\'t contain \"{p.match(login).group(1)}\"')
        else:
            print(f'[!] Login can\'t contain \'{p.match(login).group(1)}\'')
        output = False
    return output



def first_connection():
    try:
        login = input("Enter login : ")
        while not check_login(login) :
            login = input("Enter login : ")
            
            
        passwd = getpass.getpass("Enter password : ")
        confirm_passwd = getpass.getpass("Confirm password : ")
        while passwd != confirm_passwd:
            print("[!] Entries differ")
            passwd = getpass.getpass("Enter password : ")
            confirm_passwd = getpass.getpass("Confirm password : ")
            
        ph = PasswordHasher()
        greetings(login)
        hash = ph.hash(passwd)
        logins[login] = (hash, generate_key()) 
        # print(f"{login}'s key : {logins[login][1]}")
        img = qrcode.make(logins[login][1])
        img.save(f"qrcode/{login}.png")
        
    except KeyboardInterrupt: 
        print("\n[!] Exiting creation of new user")
        return None
    else: 
        print("[+] New account created")
        return login
    
    
    

def connection(): 
    try:
        login = input("Enter login : ")
        while login not in logins.keys():
            print("[!] Unknown login")
            login = input("Enter login : ")
            
            
        passwd = getpass.getpass("Enter password or TOTP : ")
        ph = PasswordHasher()
        while passwd != totp.get_totp(logins[login][1]) and passwd != totp.get_totp(logins[login][1], -1) and not ph.verify(logins[login][0], passwd):
            print("[!] Incorrect password")
            passwd = getpass.getpass("Enter password : ")
        
    except KeyboardInterrupt: 
        print("\n[!] Exiting connection")
        return None
    else: 
        print("[+] New account created")
        return login
    
    
def greetings(name):
    if name != None: 
        if name not in logins.keys():
            print(f"Welcome {name} !")    
        else: 
            print(f"Hello {name}, good to see you back !")
    else: 
        print("[!] Greeting None user")
        # print("[!] Exiting")
        # shutdown()
        
        
def start_up():
    global master_passwd
    
    master_passwd = getpass.getpass("Enter master password : ")
    counter = 0
    
    ph = PasswordHasher()
    while not ph.verify(master_hash, master_passwd) and counter != 2: 
        if counter == 1: 
            print(f"[!] Wrong password, try again ({2-counter} try left)")
        else : 
            print(f"[!] Wrong password, try again ({2-counter} tries left)")
        master_passwd = getpass.getpass("Enter master password : ")
        counter += 1

    if counter == 2: 
        print("[!] Master authentification failed")
        exit()

    print("[+] Master password accepted")
    
    if exists('logins.txt'):
        print("[+] Decrypting login file")
        with open("logins.txt", "r") as f: 
            lines = f.readlines()
        aes = AES.new((master_passwd+master_hash)[0:16], AES.MODE_CBC, (master_hash+master_passwd)[-16:])    
        for line in lines: 
            login, user_hash, c_user_key = line.split(":")
            logins[login] = (user_hash, aes.decrypt(bytes.fromhex(c_user_key)).decode('utf-8'))
            
        
    
        
def shutdown(): 
    print("[+] Encrypting login file")
    aes = AES.new((master_passwd+master_hash)[0:16], AES.MODE_CBC, (master_hash+master_passwd)[-16:])
    with open("logins.txt", "w") as f: 
        for key in logins.keys(): 
            c_user_key = aes.encrypt(logins[key][1]) 
            f.write(f"{key}:{logins[key][0]}:{c_user_key.hex()}\n")            
    print("[+] Done")
    exit()
        
    
    
    
    
if __name__ == "__main__":
    start_up()
    try: 
        name = ""
        while name != None :
            name = first_connection()
            if name != None: 
                name = connection()
                greetings(name)
    except KeyboardInterrupt: 
        shutdown()
    else: 
        shutdown()
        exit(0)
    