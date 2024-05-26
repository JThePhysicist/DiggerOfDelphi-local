import os
import argparse
from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key().decode('utf-8')

def load_secrets(file_path):
    secrets = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    secrets[key] = value
    return secrets

def save_secrets(file_path, secrets):
    with open(file_path, 'w') as file:
        for key, value in secrets.items():
            file.write(f"{key}={value}\n")

def main():
    parser = argparse.ArgumentParser(description='Generate and store an encryption key in a secrets file.')
    parser.add_argument('-f', '--secrets_file', default='secrets.env', help='Path to the secrets file (default: secrets.env)')
    parser.add_argument('-k', '--key_name', default='ENCRYPTION_KEY', help='Name of the key to store in the secrets file (default: ENCRYPTION_KEY)')
    args = parser.parse_args()

    secrets_file = args.secrets_file
    key_name = args.key_name

    # Load existing secrets
    secrets = load_secrets(secrets_file)

    # Generate a new key
    new_key = generate_key()

    # Check if the key already exists and ask for overwrite permission
    if key_name in secrets:
        overwrite = input(f"{key_name} already exists. Do you want to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("Keeping the existing key.")
            return

    # Update the secrets dictionary with the new key
    secrets[key_name] = new_key

    # Save the updated secrets back to the file
    save_secrets(secrets_file, secrets)

    print(f"{key_name} has been updated in {secrets_file}")

if __name__ == "__main__":
    main()
