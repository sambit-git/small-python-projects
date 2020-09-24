import os
from cryptography.fernet import Fernet, InvalidToken
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecretTxt:
    def __init__(self, password):
        self.password = password.encode()
        self.key = self.generate_key()
        self.file = "secret.txt"
    
    def generate_key(self):
        salt = b"Salt_"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
    
    def validate_key(self):
        if not os.path.exists(self.file):
            return True
        f = Fernet(self.key)
        with open(self.file, 'r') as fle:
            txt = fle.read()
        
        try:
            txt = f.decrypt(txt.encode())
            return True
        except InvalidToken as e:
            print("\nIncorrect Password\n",e)
            return False
    
    def write_secret_txt(self, txt):
        txt = f"{'-'*80}\n{txt}\n{'-'*80}\n"
        f = Fernet(self.key)
        if not os.path.exists(self.file):
            encrypted = f.encrypt(txt.encode()).decode()
        else:
            if self.validate_key():
                content = self.view_secret_file()
                content += ("\n"+txt)
                content = content.encode()
                encrypted = f.encrypt(content).decode()
                
                with open(self.file, 'w') as fle:
                    fle.write(encrypted+"\n")
                print("Saved Successfully!\n")

    def view_secret_file(self):
        if not os.path.exists(self.file):
            return "\nYou've not saved anything yet to view!\n"
        if self.validate_key():
            with open(self.file, 'r') as fle:
                txt = fle.read()
            # print("\n",txt,"\n")
            f = Fernet(self.key)
            txt = f.decrypt(txt.encode()).decode()
            return txt


if __name__ == "__main__":
    print("\nPlease Provide your password.")
    print("If not created till now, provide the password you want to use or else use your old password")
    print("Note: If you loose your password then you will not be able to retrive the previous content again.\n")
    password = input("\nProvide your password: ")
    secret = SecretTxt(password)
    print('\nChoose "r" or "w" to read the secret file or write into the secret file.\n')
    again = 'y'
    while again.lower() == 'y':
        choice = input("\nYour choice (r/w): ")
        if choice.lower() == "r":
            print(secret.view_secret_file())
        elif choice.lower() == "w":
            txt = input("\nProvide your text: ")
            secret.write_secret_txt(txt)
        else:
            print("\nWrong Input! Please try again.\n")
        
        for i in range(3):
            again = input("\nTry again (y/n): ")
            if again.lower() not in ['y', 'n']:
                print("\nWrong Input!")
            else:
                break
        