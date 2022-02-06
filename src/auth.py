import getpass, os, time
import os.path  
import re
from Crypto.Cipher import AES
from argon2 import PasswordHasher
import argon2
from totp import get_totp
from hmac import digest 
import qrcode
import base64

master_hash = "$argon2id$v=19$m=65536,t=3,p=4$8CJrekUuCG7jD62OFJC/Wg$x0LFj8AUAEWlzhNSCk7oS7hLJpjtnbeQBjvPv3yM2T4"

master_passwd = ""

def generate_key(): 
    return os.urandom(32).hex()


def encrypt_key(key):
    global master_hash
    global master_passwd
    aes = AES.new((master_passwd + master_hash)[0:16], AES.MODE_CBC, (master_hash + master_passwd)[-16:])
    return aes.encrypt(key).hex()

def decrypt_key(key):
    global master_hash
    global master_passwd
    aes = AES.new((master_passwd+master_hash)[0:16], AES.MODE_CBC, (master_hash+master_passwd)[-16:])
    return aes.decrypt(bytes.fromhex(key)).decode('utf-8')


def get_qrcode(user): 
    base32key = base64.b32encode(bytes.fromhex(decrypt_key(get_credentials(user)[1]))).decode('utf-8')
    qrcode_str = f"otpauth://totp/3S:{user}?secret={base32key}&issuer=3S&algorithm=SHA1&digits=6&period=30"
    return qrcode.make(qrcode_str)




def get_session_id(user, now=0): 
    session_id = digest(bytes.fromhex(get_credentials(user)[1]), (int(time.time()/420)+now).to_bytes(8, 'big'), 'sha512')
    return session_id.hex()[:48]

def verify_session_id(user, sid):
    return sid == get_session_id(user) or sid == get_session_id(user, -1)





def check_login(login):
       
    if exists(login): 
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
    
    l, u, p, d = 0, 0, 0, 0
    if (len(passwd) >= 10):
        for i in passwd:
            if (i.islower()):
                l+=1            
    
            if (i.isupper()):
                u+=1            
    
            if (i.isdigit()):
                d+=1            
    
            if(i=='@' or i=='$' or i=='_' or i=='?'or i=='!'):
                p+=1
    else: 
        return '', 4, 'Password must be at least 10 characters long'
    
    if l + p + u + d != len(passwd):
        return '', 4, 'Password contains invalid character'
    
    if l < 1: 
        return '', 4, 'Password must contain at least one lowercase letter'
        
    if u < 1: 
        return '', 4, 'Password must contain at least one uppercase letter'
    
    if d < 1: 
        return '', 4, 'Password must contain at least one digit'
    
    if p < 1: 
        return '', 4, 'Password must contain at least one special character'
    
    
    if passwd != confirm_passwd: 
        return '', 3, 'Entries differ'
        
    ph = PasswordHasher()
    hash = ph.hash(passwd)
    
    with open("logins.txt", 'a') as f: 
        f.write(f"{login}:{hash}:{encrypt_key(generate_key())}\n")


    return login, 0, ''    
    
    
    

def connection(login, passwd, totp): 

    if not exists(login): 
        return '', 5, 'Non-existent login'
    
            
    user_hash, c_user_key = get_credentials(login)    
        
    if len(passwd) != 0: 
        ph = PasswordHasher()
        try: 
            if not ph.verify(user_hash, passwd):
                return '', 6, 'Invalid password'
        except argon2.exceptions.VerifyMismatchError: 
            return '', 6, 'Invalid password'
    else: 
        if totp != get_totp(decrypt_key(c_user_key)) and totp != get_totp(decrypt_key(c_user_key), -1): 
            return '', 7, 'Invalid TOTP'
        
    return login, 0, 'Glad to see you back !'
    

        
        
def start_up():
    global master_passwd
    
    master_passwd = getpass.getpass("[ + ] Enter master password : ")
    counter = 0
    
    ph = PasswordHasher()
    authenticated = False
    while not authenticated and counter != 2: 
        try: 
            authenticated = ph.verify(master_hash, master_passwd)
        except:
            authenticated = False
            if counter == 1: 
                print(f"[ ! ] Wrong password, try again ({2-counter} try left)")
            else : 
                print(f"[ ! ] Wrong password, try again ({2-counter} tries left)")
            master_passwd = getpass.getpass("[ + ] Enter master password : ")
            counter += 1

    if counter == 2: 
        print("[ ! ] Master authentification failed")
        exit()

    print("[ + ] Master password accepted")
        
            
        
    
        
def shutdown(): 
    print("\n[ + ] Server shut down ")
    os.system("rm -f static/qrcode/*")
    print("[ + ] Shutting down ")
    exit()
        
    

def get_credentials(user):
    with open("logins.txt", 'r') as f:
        line = f.readline()
        while line: 
            login, user_hash, c_user_key = line.split(":")
            if login == user: 
                return user_hash, c_user_key
            else: 
                line = f.readline()
                
def exists(user): 
    if os.path.exists('logins.txt'): 
        with open('logins.txt', 'r') as f: 
            line = f.readline()
            while line:
                login, _, __ = line.split(':')
                if login == user:
                    return True
                line = f.readline()
    return False