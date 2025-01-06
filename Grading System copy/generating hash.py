from werkzeug.security import generate_password_hash

# Your plaintext password
password = "COEPSU777@,"

# Generate the hash using pbkdf2:sha256
hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

print("Hashed Password:", hashed_password)