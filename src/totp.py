#!/usr/bin/python3
import os 
import time
import hmac

x = 1


def get_totp(key, timestamp): 
    return hmac.digest(key, timestamp.to_bytes(8, 'big'), 'sha512')[0:8]

if __name__ == "__main__":
    
    key = os.urandom(24)
    print(f"Key : {key.hex()}")
    
    for i in range(5):
        print("-"*50)
        timestamp = int(time.time()/x)
        print(f"Timestamp : {hex(timestamp)}")
        thash = get_totp(key, timestamp)
        print(f"TOTP : {thash.hex()}")
        time.sleep(x)