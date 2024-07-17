import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

class PasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Password Entry")
        self.geometry("300x150")

        self.label = ctk.CTkLabel(self, text="Please enter your password:")
        self.label.pack(pady=10)

        self.entry = ctk.CTkEntry(self, show='*')
        self.entry.pack(pady=10)

        self.button = ctk.CTkButton(self, text="Submit", command=self.on_submit)
        self.button.pack(pady=10)

        self.password = None

    def on_submit(self):
        self.password = self.entry.get()
        self.destroy()

def on_password_request():
    dialog = PasswordDialog(root)
    root.wait_window(dialog)
    password = dialog.password
    if password:
        messagebox.showinfo("Password Entered", "Password entered successfully!")
    else:
        messagebox.showwarning("No Password", "You did not enter a password.")

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("300x150")

    button = ctk.CTkButton(root, text="Enter Password", command=on_password_request)
    button.pack(pady=20)

    root.mainloop()
