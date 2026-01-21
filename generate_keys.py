import bcrypt

# Password yang mau kita pakai
passwords = ['hr123', 'staf123']

print("--- COPY KODE HASH DI BAWAH INI KE config.yaml ---")

for pw in passwords:
    # Ubah password jadi bytes, lalu hash
    hashed = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
    
    # Print hasilnya dalam bentuk string
    print(f"Password '{pw}': {hashed.decode('utf-8')}")