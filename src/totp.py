import os 
import time
import hmac

x = 30


def get_totp(key, now=0): 
    hash = hmac.digest(bytes(key, 'utf-8'), (int(time.time()/x)+now).to_bytes(8, 'big'), 'sha512')
    return "%.6d" %(int.from_bytes(hash, 'big')%(10**6))

if __name__ == "__main__":
    
    key = input(f"Key : ")
    try: 
        while True: 
            input()
            print(f"TOTP : {get_totp(key)}", end='')
    except KeyboardInterrupt: 
        print("\n[+] Goodbye")
        exit()
        