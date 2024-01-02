import rsa
import cryptography
from cryptography.fernet import Fernet
from flask import Flask, render_template, request
from rsa import PublicKey
import mysql.connector
import db_connect






app = Flask(__name__)

import db_connect

db_config =  mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="System_security"
)


# Create a cursor for database operations

cursor = db_config.cursor()

# Generating the encryption key and saving it to a file
def generate_key_S():
    key = Fernet.generate_key()
    with open("Secret.key", "wb") as key_file:
        key_file.write(key)
        
        
def generate_key_A():
    publickey, privatekey = rsa.newkeys(512)

    with open('public.pem', 'wb') as f:
        f.write(publickey.save_pkcs1())

    with open('private.pem', 'wb') as f:
        f.write(privatekey.save_pkcs1())


# Loading the encryption key from the file
def load_key_S():
    return open("Secret.key", "rb").read()


def load_key_A():
    with open('public.pem', 'rb') as f:
        public_key = rsa.PublicKey.load_pkcs1(f.read())
    
    with open('private.pem', 'rb') as f:
        private_key = rsa.PrivateKey.load_pkcs1(f.read())
    return public_key, private_key



@app.route('/generate_key_S', methods=['POST'])
def generate_and_display_key_S():
    generate_key_S()
    g = load_key_S().decode('utf-8')  # Decode the key to remove 'b' prefix
    return render_template('symmentric.html', output=g)


@app.route('/generate_key_A', methods=['POST'])
def generate_and_display_key_A():
    generate_key_A()
    public_key_data,private_key_data = load_key_A() 
    return render_template('Asymmentric.html', public_key=public_key_data, private_key=private_key_data ,user_names=db_connect.users_names,column_names=db_connect.column_names)



@app.route('/Encrypt_Decrypt_S', methods=['GET', 'POST'])
def encrypt_decrypt_S():
    output_text = ""

    if request.method == 'POST':
        choice = request.form.get('action')
        input_text = request.form.get('input_text')
        key = request.form.get('secret_key')

        try:
            key = key.encode('utf-8')  # Ensure the key is bytes
            f = Fernet(key)            # Create a Fernet object with the key
        except Exception as e:
            return render_template('symmentric.html', output_text=f"Key error: {e}")

        if input_text.strip() == "":
            output_text = "No input is given."
        elif choice == 'Encrypt':
            output_text = f.encrypt(input_text.encode()).decode()
        elif choice == 'Decrypt':
            decrypted_data = f.decrypt(input_text.encode())
            output_text = decrypted_data.decode("utf-8")

    return render_template('symmentric.html', output_text=output_text)









@app.route('/encrypt_decrypt_A', methods=['POST'])
def encrypt_decrypt_A():
    output_text = ""
    
    if request.method == 'POST':
        choice = request.form.get('action')
        key = request.form.get('key')
        user = request.form.get('user')
        Attribute = request.form.get('Attribute')

        # Load the public and private keys (make sure to implement load_key_A)
        public_key_data, private_key_data = load_key_A()

        if choice == 'Encrypt':
            if key.strip() != "":
                # Fetch the selected attribute from the database
                cursor.execute("SELECT {} FROM users WHERE firstname = %s".format(Attribute), (user,))
                selected = cursor.fetchone()

                if selected:
                    selected_value = selected[0]
                    # Encrypt the selected value
                    #encryption = rsa.encrypt(selected_value.encode(), public_key_data)
                    #output_text = encryption.hex()
                    
                    global encryption
                    global encryption2

                    # Encode the selected value
                    encryption = rsa.encrypt(selected_value.encode(), public_key_data)
                    output_text = encryption.hex()
                    encryption2=output_text
                    
                    # Update the database with the encrypted value using parameterized query
                    cursor.execute("UPDATE users SET {} = %s WHERE firstname = %s".format(Attribute), (output_text, user))
                    db_config .commit()
                    
                    output_text2 = ' YOU HAVE SUCCESSFULLY ENCRYPTED                                  HERE IS THE ENCRYPTED ATTRIBUTE VALUE    :         ' + output_text 
                else:
                    output_text = 'User not found or selected attribute does not exist.'
            else:
                output_text = 'The given public key is incorrect. Please check and try again.'
        
        elif choice == 'Decrypt':
            
            if 'encryption2' in globals():  # Check if 'encryption' variable is defined
                # Decrypt the previously encrypted value
                
                decryption = rsa.decrypt(bytes.fromhex(encryption2), private_key_data).decode()
                output_text = decryption
                output_text2 = ' YOU HAVE SUCCESSFULLY DECRYPTED     ' + decryption
                
                # Update the database with the decrypted value
                cursor.execute("UPDATE users SET {} = %s WHERE firstname = %s".format(Attribute), (output_text, user))
                db_config.commit()
            else:
                output_text = 'No encryption data available for decryption.'


    #return render_template('Asymmentric.html', output_text= output_text2 ,user_names=db_connect.users_names,column_names=db_connect.column_names, public_key=public_key_data, private_key=private_key_data )
    return render_template('Asymmentric.html', output_text=output_text2 if choice == 'Decrypt' else output_text2, user_names=db_connect.users_names, column_names=db_connect.column_names, public_key=public_key_data if choice == 'Encrypt' else None, private_key=private_key_data if choice == 'Encrypt' else None)




@app.route('/Asymmetric')
def Asymmentric():
    return render_template('Asymmentric.html',user_names=db_connect.users_names,column_names=db_connect.column_names)

@app.route('/symmentric')
def symmentric():
    return render_template('symmentric.html' ,user_names=db_connect.users_names ,column_names=db_connect.column_names)


@app.route('/home', methods=['POST'])
def home1():
    return render_template('home.html')

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000,debug=True)
