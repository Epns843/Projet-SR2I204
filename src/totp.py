import os 
import time
import hmac

x = 30


def get_totp(key, timestamp): 
    hash = hmac.digest(key, timestamp.to_bytes(8, 'big'), 'sha512')
    return "%.6d" %(int.from_bytes(hash, 'big')%(10**6))

if __name__ == "__main__":
    
    key = os.urandom(24)
    print(f"Key : {key.hex()}")
    
    for i in range(10):
        print("-"*50)
        timestamp = int(time.time()/x)
        print(f"Timestamp : {hex(timestamp)}")
        hash = get_totp(key, timestamp)
        print(f"TOTP : {hash}")
        time.sleep(x)
        