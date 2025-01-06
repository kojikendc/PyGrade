import hashlib
import binascii
import base64

# Sample stored hash (make sure this is accurate from your database)
stored_hash = "scrypt:32768:8:1$CdqM0y3MAT2VQU4n$0a78d3fb3b6cda408f76afe44561488f0a964792088022c1e99688ee4729bc603bb3461d3d6b536e73545dd3ebd5a244a087cbabe590b5225da28ba891e69d30"

# Clean up the stored hash to remove any leading/trailing spaces or newlines
stored_hash = stored_hash.strip()

# Print the stored hash to see its format
print(f"Stored hash: {stored_hash}")

# Split the stored hash into parts
parts = stored_hash.split('$')

# Check if there are exactly 4 parts
if len(parts) != 4:
    print(f"Error: The stored hash doesn't have the expected format (4 parts). It has {len(parts)} parts.")
else:
    # Extract the components
    algorithm, params, salt_base64, stored_password_hash = parts
    print(f"Algorithm: {algorithm}")
    print(f"Params: {params}")
    print(f"Salt (base64): {salt_base64}")
    print(f"Stored password hash: {stored_password_hash}")
    
    # Extract parameters (cost, block_size, parallelization)
    cost, block_size, parallelization = map(int, params.split(':'))
    
    # Decode the salt from base64
    salt = base64.b64decode(salt_base64)
    
    # Input password to verify
    input_password = "JAYPEN"  # Replace with the password you are testing
    
    # Derive the key using scrypt with the extracted parameters
    derived_key = hashlib.scrypt(
        input_password.encode('utf-8'),
        salt=salt,
        n=cost,
        r=block_size,
        p=parallelization,
        dklen=len(binascii.unhexlify(stored_password_hash))
    )
    
    # Convert derived key to hex and compare with stored hash
    derived_key_hex = binascii.hexlify(derived_key).decode('utf-8')
    print(f"Stored password hash: {stored_password_hash}")
    print(f"Derived password hash: {derived_key_hex}")
    
    # Compare the derived key with the stored hash
    if stored_password_hash == derived_key_hex:
        print("Password is correct!")
    else:
        print("Password is incorrect.")
