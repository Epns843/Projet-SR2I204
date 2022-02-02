import getpass, os, hashlib
from os.path import exists 
import re
from Crypto.Cipher import AES
import qrcode 
from argon2 import PasswordHasher
import argon2
from totp import get_totp
from hmac import digest 


master_hash = "$argon2id$v=19$m=65536,t=3,p=4$8CJrekUuCG7jD62OFJC/Wg$x0LFj8AUAEWlzhNSCk7oS7hLJpjtnbeQBjvPv3yM2T4"

logins = dict()

master_passwd = ""

def generate_key(): 
    return os.urandom(24).hex()



def check_login(login):
       
    if login in logins.keys():
        return False, 1, "Login already used"
        
    p =  re.compile(r'.*([\W]+).*')
    if p.match(login) != None:
        if p.match(login).group()[1] == "'": 
            error = f'Login can\'t contain \"{p.match(login).group(1)}\"'
        else:
            error = f'Login can\'t contain \'{p.match(login).group(1)}\''
        return False, 2, error
    return True, 0, ''



def first_connection(login, passwd, confirm_passwd):

    if not check_login(login)[0]:
        return '', check_login(login)[1], check_login(login)[2]
    
    if passwd != confirm_passwd: 
        return '', 3, 'Entries differ'
        
    ph = PasswordHasher()
    hash = ph.hash(passwd)
    logins[login] = (hash, generate_key()) 

    img = qrcode.make(logins[login][1])
    h = digest(logins[login][1].encode("utf-8"), login.encode("utf-8"), 'sha512').hex()[:32]
    img.save(f"static/qrcode/{login}:{h}.png")

    return login, 0, ''    
    
    
    

def connection(login, passwd, totp): 

    if login not in logins.keys():
        return '', 5, 'Non-existent login'            
            
    if len(passwd) != 0: 
        ph = PasswordHasher()
        try: 
            if not ph.verify(logins[login][0], passwd):
                return '', 6, 'Invalid password'
        except argon2.exceptions.VerifyMismatchError: 
            return '', 6, 'Invalid password'
    else: 
        if totp != get_totp(logins[login][1]) and totp != get_totp(logins[login][1], -1): 
            return '', 7, 'Invalid TOTP'
        
    return login, 0, 'Glad to see you back !'
    
    
    
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
    
    master_passwd = getpass.getpass("[ + ] Enter master password : ")
    counter = 0
    
    ph = PasswordHasher()
    while not ph.verify(master_hash, master_passwd) and counter != 2: 
        if counter == 1: 
            print(f"[ ! ] Wrong password, try again ({2-counter} try left)")
        else : 
            print(f"[ ! ] Wrong password, try again ({2-counter} tries left)")
        master_passwd = getpass.getpass("Enter master password : ")
        counter += 1

    if counter == 2: 
        print("[ ! ] Master authentification failed")
        exit()

    print("[ + ] Master password accepted")
    
    if exists('logins.txt'):
        print("[   ] Decrypting login file", end='')
        with open("logins.txt", "r") as f: 
            lines = f.readlines()
        aes = AES.new((master_passwd+master_hash)[0:16], AES.MODE_CBC, (master_hash+master_passwd)[-16:])    
        for line in lines: 
            login, user_hash, c_user_key = line.split(":")
            logins[login] = (user_hash, aes.decrypt(bytes.fromhex(c_user_key)).decode('utf-8'))
        print("\r[ + ] Login file decrypted   ")
        
            
        
    
        
def shutdown(): 
    print("[ + ] Server shut down ")
    print("[   ] Encrypting login file", end='')
    aes = AES.new((master_passwd+master_hash)[0:16], AES.MODE_CBC, (master_hash+master_passwd)[-16:])
    with open("logins.txt", "w") as f: 
        for key in logins.keys(): 
            c_user_key = aes.encrypt(logins[key][1]) 
            f.write(f"{key}:{logins[key][0]}:{c_user_key.hex()}\n")            
    print("\r[ + ] Login file encrypted   ")
    print("[ + ] Shutting down ")
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
    