import time, hmac

x = 30

def get_totp(key, now=0): 
    hash = hmac.digest(bytes.fromhex(key), (int(time.time()/x)+now).to_bytes(8, 'big'), 'sha1')
    offset   =  hash[19] & 0xf
    bin_code = (hash[offset]  & 0x7f) << 24| (hash[offset+1] & 0xff) << 16| (hash[offset+2] & 0xff) <<  8| (hash[offset+3] & 0xff)
    return "%.6d" %(bin_code%(10**6))



if __name__ == "__main__":
    
    key = input(f"Key : ")
    try: 
        while True: 
            input()
            print(f"TOTP : {get_totp(key)}", end='')
    except KeyboardInterrupt: 
        print("\n[+] Goodbye")
        exit()
        