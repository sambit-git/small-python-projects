import os
from cryptography.fernet import Fernet, InvalidToken
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pyttsx3


engine = pyttsx3.init()

def init_speak_engine():
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    # volume = engine.getProperty('volume')
    engine.setProperty('volume',1.0)
    # rate = engine.getProperty('rate')
    engine.setProperty('rate', 200)
def speak_msg(msg):
    engine.say(msg)
    engine.runAndWait()

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
            else:
                return False
                
        with open(self.file, 'w') as fle:
            fle.write(encrypted+"\n")
        return True

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
    init_speak_engine()
    msg = "Please Provide your password."
    print(f"\n{msg}")
    speak_msg(msg)
    msg = "If not created till now, provide the password you want to use, or else use your old password"
    print(msg)
    speak_msg(msg)
    msg = "Note: If you loose your password, then you will not be able to retrive the previous content again."
    print(f"{msg}\n")
    speak_msg(msg)
    speak_msg("Please Provide your password")
    password = input("\nProvide your password: ")
    
    secret = SecretTxt(password)
    msg = 'Choose "r", or "w" to read the secret file, or write into the secret file.'
    print(f'\n{msg}\n')
    speak_msg(msg)
    again = 'y'
    while again.lower() == 'y':
        speak_msg("Provide your choice, r to Read, and w to Write.")
        choice = input("\nYour choice (r/w): ")
        if choice.lower() == "r":
            speak_msg("You've Selected to read. Content will not be read aloud!")
            print(secret.view_secret_file())
        elif choice.lower() == "w":
            speak_msg("You've Selected to write. If your password would be wrong, we won't be able to write.")
            speak_msg("Provide yout text to be written into the secret file")
            txt = input("\nProvide your text: ")
            success = secret.write_secret_txt(txt)
            if success:
                msg = "Saved Successfully!"
                print(f"\n{msg}\n")
                speak_msg(msg)
            else:
                msg = "You've provided and incorrect password!"
                print(f"\n{msg}\n")
                speak_msg(msg)
        else:
            msg = "Wrong Input! Please try again."
            print(f"\n{msg}\n")
            speak_msg(msg)
        
        for i in range(3):
            speak_msg("Wanna continue?")
            speak_msg("Press Y to continue or N to exit")
            again = input("\nTry again (y/n): ")
            if again.lower() not in ['y', 'n']:
                print("\nWrong Input!")
                speak_msg("Wrong Input. Please Try again.")
            else:
                break
    msg = "Thank you and Bye bye!"
    speak_msg(msg)
    print(f"\n{msg}\n")