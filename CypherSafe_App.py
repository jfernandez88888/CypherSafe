import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from cryptography.fernet import Fernet
import base64
import os
import tkinter.messagebox as messagebox

# Function to load or generate encryption key
def load_or_generate_key():
    key_file = "secret.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as file:
            key = file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as file:
            file.write(key)
    return key

# Load the encryption key
key = load_or_generate_key()
cipher_suite = Fernet(key)

# Create the master window
master = Tk()
master.geometry("900x510")
master.config(bg="dimgray")
master.title("CypherSafe Password manager")

# Function to populate the listbox with files
def populate_listbox():
    file_listbox.delete(0, END)
    files = [file for file in os.listdir() if file.endswith(".txt")]
    for file in files:
        if "?" not in file:
            file_listbox.insert(END, file)

def Save():
    # Get text from entry boxes
    website = wentry.get()
    username = uentry.get()
    password = pentry.get()
    
    # Shift value for Caesar Cipher
    caesar_shift = 3
    
    # Encode to base64 formatted to UTF 8
    encoded_username = base64.b64encode(username.encode('utf-8')).decode('utf-8')
    encoded_password = base64.b64encode(password.encode('utf-8')).decode('utf-8')
    
    # Encode base64 to Caesar Cipher
    encoded_username = caesar_cipher(encoded_username, caesar_shift)
    encoded_password = caesar_cipher(encoded_password, caesar_shift)
    
    # Place all entries into a single variable
    content = f"Website: {website}\nUsername: {encoded_username}\nPassword: {encoded_password}\n\n"
    
    # Check if file already exists
    filename = f"{website}.txt"
    if os.path.exists(filename):
        # Ask for confirmation before overwriting the existing file
        confirm = messagebox.askyesno("Warning", f"A file named '{website}.txt' already exists. Overwrite?")
        if not confirm:
            return

    # Encrypt Content using a key
    encrypted_content = cipher_suite.encrypt(content.encode('utf-8'))
    
    with open(filename, "wb") as file:
        file.write(encrypted_content)
    
    populate_listbox()

# Flag to track if decryption window is open
decrypt_window_open = False

def Decrypt():
    global decrypt_window_open
    if decrypt_window_open:
        return

    selected_file = file_listbox.get(ANCHOR)
    if selected_file:
        try:
            with open(selected_file, "rb") as file:
                encrypted_content = file.read()
                decrypted_content = cipher_suite.decrypt(encrypted_content).decode('utf-8')

                # Split the decrypted content into lines
                decrypted_lines = decrypted_content.split("\n")

                # Extract website, username, and password from decrypted content
                website = decrypted_lines[0].split(": ")[1]
                encoded_username = decrypted_lines[1].split(": ")[1]
                encoded_password = decrypted_lines[2].split(": ")[1]

                # Reverse the Caesar cipher
                caesar_shift = 3
                decoded_username = caesar_cipher(encoded_username, -caesar_shift)
                decoded_password = caesar_cipher(encoded_password, -caesar_shift)

                # Decode base64
                decoded_username = base64.b64decode(decoded_username).decode('utf-8')
                decoded_password = base64.b64decode(decoded_password).decode('utf-8')

                # Create a message with decrypted information
                decrypted_message = f"Website: {website}\nUsername: {decoded_username}\nPassword: {decoded_password}\n"

                # Create a new window to display the decrypted information
                decrypt_window = Toplevel(master)
                decrypt_window.title(f"Decrypted - {selected_file}")
                text_area = Text(decrypt_window)
                text_area.insert(END, decrypted_message)
                text_area.pack()

                # Set the flag to True when the window is created
                decrypt_window_open = True

                # Define a function to reset the flag when the window is closed
                def on_close():
                    global decrypt_window_open
                    decrypt_window_open = False
                    decrypt_window.destroy()

                decrypt_window.protocol("WM_DELETE_WINDOW", on_close)
        except FileNotFoundError:
            print(f"File '{selected_file}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

def caesar_cipher(text, shift):
    result = []
    for char in text:
        if char.isalpha():
            shift_base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - shift_base + shift) % 26 + shift_base))
        else:
            result.append(char)
    return ''.join(result)

def Delete():
    selected_file = file_listbox.get(ANCHOR)
    if selected_file:
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{selected_file}'?")
        if confirm:
            try:
                os.remove(selected_file)
                populate_listbox()  # Update the listbox after deletion
            except FileNotFoundError:
                print(f"File '{selected_file}' not found.")
            except Exception as e:
                print(f"An error occurred: {e}")

# Flag to track if help window is open
help_window_open = False

def show_help():
    global help_window_open
    if not help_window_open:
        help_message = (
            "CypherSafe Password Manager\n\n"
            "Website: Enter the website name.\n"
            "Username: Enter the username for the website.\n"
            "Password: Enter the password for the website.\n\n"
            "Buttons:\n"
            "Save: Save the entered website, username, and password. The data is encrypted and saved to a file.\n"
            "Decrypt: Decrypt the selected file and display the decrypted information.\n"
            "Delete: Delete the selected file from the list.\n"
        )
        help_window = Toplevel(master)
        help_window.title("Help")
        text_area = Text(help_window, wrap='word')
        text_area.insert(END, help_message)
        text_area.pack()

        # Set the flag to True when the window is created
        help_window_open = True

        # Define a function to reset the flag when the window is closed
        def on_close():
            global help_window_open
            help_window_open = False
            help_window.destroy()

        help_window.protocol("WM_DELETE_WINDOW", on_close)


# Creates the label for the headliner
header = tk.Label(master, 
                  text='CypherSafe Password Manager', 
                  width=100, 
                  bg="gray",
                  height=3,
                  font=(6),
                  fg="black",
                  justify="center"
                  )
header.grid(row=0, 
            columnspan=3
            )

# Create label for website and entry for website
wlabel = tk.Label(master,
                  text='Website',
                  width=10,
                  height=2,
                  bg='gray'
                  )
wlabel.grid(row=1, 
            column=0,
            padx=3,
            pady=10
            )

wentry = Entry(master,)
wentry.grid(row=2, 
            column=0,
            pady=3
            )

# Create label for username and entry for username
ulabel = tk.Label(master,
                  text='Username',
                  width=10,
                  height=2,
                  bg='gray'
                  )
ulabel.grid(row=1,
            column=1,
            padx=3,
            pady=10
            )

uentry = Entry(master, )
uentry.grid(row=2, 
            column=1,
            pady=3
            )

# Create label for password and entry for password
plabel = tk.Label(master,
                  text='Password',
                  width=10,
                  height=2,
                  bg='gray'
                  )
plabel.grid(row=1,
            column=2,
            padx=3,
            pady=10
            )

pentry = Entry(master, )
pentry.grid(row=2, 
            column=2,
            pady=3
            )

# Save Button
sbutton = tk.Button(master, 
                    text="Save", 
                    command=Save,
                    activebackground="dimgray", 
                    activeforeground="dimgray",
                    anchor="center",
                    font=(6),
                    height=2,
                    justify="center",
                    overrelief="raised",
                    width=10,
                    )
sbutton.grid(row=3,
             column=0,
             padx=3,
             pady=10,
             )

# Create a listbox to display the files
file_listbox = Listbox(master, 
                       height=15, 
                       width=40, 
                       bg="white", 
                       fg="black", 
                       font=("Arial", 12))

file_listbox.grid(row=4, 
                  column=0, 
                  columnspan=3, 
                  pady=10)

# Decrypt Button
dbutton = tk.Button(master, 
                    text="Decrypt", 
                    command=Decrypt,
                    activebackground="dimgray", 
                    activeforeground="dimgray",
                    anchor="center",
                    font=(6),
                    height=2,
                    justify="center",
                    overrelief="raised",
                    width=10,
                    )
dbutton.grid(row=3,
             column=2,
             padx=3,
             pady=10,
             )

# Delete Button
dbutton = tk.Button(master, 
                    text="Delete", 
                    command=Delete,
                    activebackground="dimgray", 
                    activeforeground="dimgray",
                    anchor="center",
                    font=(6),
                    height=2,
                    justify="center",
                    overrelief="raised",
                    width=10,
                    )
dbutton.grid(row=3,
             column=1,
             padx=3,
             pady=10,
             )

# Help Button
help_button = tk.Button(master, 
                        text="?", 
                        command=show_help,
                        activebackground="dimgray", 
                        activeforeground="dimgray",
                        anchor="center",
                        font=(6),
                        height=2,
                        justify="center",
                        overrelief="raised",
                        width=2,
                        )
help_button.grid(row=5,
                 column=2,
                 sticky='e',
                 padx=5,
                 pady=5)

# Populate the listbox when the application starts
populate_listbox()
#loop main window
mainloop()
