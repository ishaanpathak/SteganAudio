# ===========================[ Program Information ]===========================

# Program: SteganAudio
# Version: 1.0
# Author : https://github.com/ishaanpathak
# Project: https://github.com/ishaanpathak/SteganAudio

# =================================[ Imports ]=================================

import os
from sys import platform,stdin
import getpass
import wave
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from colorama import init
from termcolor import colored

# ======================[ Configuration/Initialization ]=======================
init()

# =============================[ Visual Functions ]============================

def clearTerminal():
    if 'win32' in platform:
        os.system('cls')
    else:
        os.system('clear')

def printBanner():
    banner = '''
  ____  _                            _             _ _       
 / ___|| |_ ___  __ _  __ _ _ __    / \  _   _  __| (_) ___  
 \___ \| __/ _ \/ _` |/ _` | '_ \  / _ \| | | |/ _` | |/ _ \ 
  ___) | ||  __/ (_| | (_| | | | |/ ___ \ |_| | (_| | | (_) |
 |____/ \__\___|\__, |\__,_|_| |_/_/   \_\__,_|\__,_|_|\___/ 
                |___/ \033[1;91mHide Secret Messages inside Audio files\033[0m\n'''
    clearTerminal()
    print(banner[1:])

# ===========================[ Encryption Functions ]==========================

def createRandomKey():
    key = Fernet.generate_key()
    print(colored("\n[SUCCESS]","green"),"Created Key: ",key)
    print(colored("\n[WARNING]","red"),"Store Key for Decrypting!")
    return key

def saveKeyToFile(filename,key):
    file = open(filename,'wb')
    file.write(key)
    file.close()

def readKeyFromFile(filename):
    file = open(filename,'rb')
    key = file.read()
    file.close()
    return key

def createPasswordBasedKey():
    print(colored("\n[NOTE]","yellow"),"The password will not be shown while typing.\n       Type it and press Enter.")
    password = getpass.getpass("\n[INPUT] Enter Password for Encryption: ").encode()
    choice = input("\n[INPUT] Choose Salt Type:\n   [1] Custom\n   [2] Random")
    if choice=="1":
        salt = input("\n[INPUT] Enter Custom Salt: ").encode()
    else:
        salt = os.urandom(16)
    print(colored("\n[SUCCESS]","green"),"Created Salt:",salt)
    print(colored("\n[WARNING]","red"),"Store the salt somewhere for creating the same key again!")
    print(colored("\n[NOTE]","yellow"),"Please provide complete location for saving the Salt File: ")
    saltPath = input("> ")
    if os.path.exists(saltPath):
      print(colored("\n[NOTE]","red"),"The file already exists, would you like to replace it?")
      if input("[Y/N] > ").upper() != 'Y':
        print(colored("\n[NOTE]","yellow"),"Please provide a name for saving the Salt File: ")
        saltPath = input("> ")
    with open(saltPath + '.salt','wb') as file:
      file.write(salt)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    print(colored("\n[SUCCESS]","green"),"Created Key: ",key)
    return key

def encryptText(text,key):
    f = Fernet(key)
    return f.encrypt(text.encode())

def chooseEncryptionType():
    choice = input("\n[INPUT] Select type of Encryption Key:\n   [1] Random Key\n   [2] Password Based Key\nSelection > ")
    if choice=="1":
        return createRandomKey()
    else:
        return createPasswordBasedKey()

def encrypt(string):
  choice = input('\n[INPUT] Select option:\n[1] Use a pre-made key file for encryption\n[2] Create a new Key File and use that\n> ')
  if choice=='1':
    keypath = input("\n[INPUT] Complete location of the key file (including file extension): ")
    if os.path.exists(keypath):
      key = readKeyFromFile(keypath)
      return encryptText(string, key)
    else:
      print(colored("\n[ERROR]","red"),"The path you provided isn't either correct or doesn't exist")
  elif choice=='2':
    key = chooseEncryptionType()
    print(colored("\n[WAIT]","yellow"),"Saving the key...")
    filename = input("\n[INPUT] Complete location for saving the generated key file: ")
    saveKeyToFile(filename, key)
    return(encryptText(string, key))
  else:
    print(colored("\n[ERROR]","red"),"You can either choose 1 or 2. {} isn't a valid choice".format(choice))
    if input("\n[INPUT] Try again? [Y/N]: ").upper() == 'Y':
      encrypt(string)

# ===============================[ Decryption ]================================

def decryptText(text,key):
    try:
        f = Fernet(key)
        decrypted = f.decrypt(text.encode())
    except Exception:
        print(colored("[ERROR]","red"),"Possible reasons for Error:\n  [1] Provided Key is not the correct key\n  [2] The Audio file is somehow corrupted")
        exit()
    return decrypted

def recreateKeyFromSalt():
    print(colored("\n[NOTE]","yellow"),"This function assumes you have the Salt & the Password\nthat was used to Encrypt the original message")
    password = getpass.getpass("\n[INPUT] Decryption Password: ").encode()
    saltFile = input("\n[INPUT] Complete Location for the Stored Salt File: ").replace('"','')
    if not os.path.exists(saltFile):
        print(colored("\n[ERROR]","red"),"The location you provided doesn't seem to be valid. Please try again.")
        exit()
    with open(saltFile,'rb') as file:
        salt = file.read()
    print(colored("\n[SUCCESS]","green"),"Salt Loaded")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    try:
        key = base64.urlsafe_b64encode(kdf.derive(password))
    except Exception:
        print(colored("\n[ERROR]","red"),"The salt file is either corrupted or Invalid")
        exit()
    print(colored("\n[SUCCESS]","green"),"The decryption key has been created successfully!")
    return key

def decrypt(encrypted_message):
    print(colored("\n[NOTE]","yellow"),"To decrypt the message, you need one of the following:\n  [1] Stored Key File\n  [2] Salt File + Password")
    choice = int(input("[INPUT] Which one of the above do you have? [Enter 1 or 2]: "))
    if choice == 1:
        keyFile = input("\n[INPUT] Complete location of the key file: ").replace('"','')
        if os.path.exists(keyFile):
            key = readKeyFromFile(keyFile)
            output = decryptText(encrypted_message,key)
        else:
            print(colored("\n[ERROR]","red"),"The location for the key you provided is invalid. Check the path and try again.")
    elif choice == '2':
        key = createPasswordBasedKey()
        output = decryptText(encrypted_message,key)
    else:
        print(colored("\n[ERROR]","red"),"{} isn't a valid option. Please choose among 1 and 2 only.")
        if input("\nTry again? [Y/N] > ").upper() == 'Y':
            decrypt(encrypted_message)
    return output

# ==============================[ Main Functions ]=============================

def embed_into_audio(input_audio,message,output_audio):
    print(colored("\n[PROCESSING]","yellow"),"The Audio is being processed, Please Wait...")
    waveObject = wave.open(input_audio, mode='rb')
    frameBytes = bytearray(list(waveObject.readframes(waveObject.getnframes())))    
    message = message + int((len(frameBytes)-(len(message)*8*8))/8) *'#'
    bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in message])))
    for i, bit in enumerate(bits):
        frameBytes[i] = (frameBytes[i] & 254) | bit
    frameModified = bytes(frameBytes)
    with wave.open(output_audio,'wb') as output:
        output.setparams(waveObject.getparams())
        output.writeframes(frameModified)
    waveObject.close()
    print(colored("\n[SUCCESS]","green"),"Embedded message into Audio File successfully!")

def extract_from_audio(input_audio, encrypted):
    print(colored("\n[PROCESSING]","yellow"),"The Audio is being processed, Please Wait...")
    waveObject = wave.open(input_audio, mode='rb')
    frameBytes = bytearray(list(waveObject.readframes(waveObject.getnframes())))
    extracted = [frameBytes[i] & 1 for i in range(len(frameBytes))]
    string = "".join(chr(int("".join(map(str,extracted[i:i+8])),2)) for i in range(0,len(extracted),8))
    message = string.split("###")[0]
    if encrypted: message = decrypt(message).decode()
    print(colored("\n[SUCCESS]","green"),"Your embedded message is as follows:\n\n{}\n".format(message))

# ==============================[ I/O Functions ]==============================

def multiLineInput():
    print(colored("\n[NOTE]","yellow"),"Multi Line Input has started, to stop Input, Enter a new Blank Line\nand press CTRL+Z (or CTRL+D if that doesn't work) and press Enter")
    msg = stdin.readlines()
    output = ""
    for i in range(len(msg)):
        output = output + msg[i]
    return output[:-2]

# ==============================[ Main Function ]==============================

if __name__=="__main__":
    printBanner()
    print(colored("[CHOICE]","yellow"),"What would you like to do?\n   [1] Embed Message into an Audio File\n   [2] Extract Message from Audio File")
    choice = int(input("Selection > "))
    if choice == 1:
        printBanner()
        audiofile = input("\n[INPUT] Complete Location of Input Audio File: ").replace('"','')
        typechoice = int(input("\n[CHOICE] Choose type of Message:\n  [1] Single Line Message\n  [2] Multiline Message\n > "))
        if typechoice == 1:
            message = input("\n[INPUT] Enter the message you want to hide: ")
        elif typechoice == 2:
            message = multiLineInput()
        else:
            print(colored("\n[ERROR]","red"),"{} is not a valid option".format(typechoice))
        outputfile = input("\n[INPUT] Complete Location for Output Audio File: ").replace('"','')
        if input("\n[INPUT] Do you want to Encrypt the Message?\n[Y/N] > ").upper() == 'Y':
            message = encrypt(message).decode()
        try:
            embed_into_audio(audiofile,message,outputfile)
        except:
            print(colored("\n[ERROR]","red"),"An unhandled error has ocurred, please try again!")
            quit()
    elif choice == 2:
        printBanner()
        audiofile = input("\n[INPUT] Complete Location of Input Audio File: ").replace('"','')
        choice = input("\n[INPUT] Is the message Encrypted? [Y/N]: ")
        encrypted = False
        if choice.upper() == 'Y':
            encrypted = True
        elif choice.upper() == 'N' or choice == None:
            encrypted = False
        else:
            print(colored("\n[ERROR]","red"),"{} isn't a valid input, exitting program...")
            exit()
        extract_from_audio(audiofile,encrypted)
    elif choice == 99:
        printBanner()
        print(" Exit code received, Thank you for using SteganAudio!\n")
    else:
        print(colored("\n[ERROR]","red"), choice, "isn't a valid choice, exiting program...")