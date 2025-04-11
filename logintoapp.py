import tkinter as tk
from tkinter import ttk, messagebox

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Admin Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # Center the window
        window_width = 400
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill="both")

        # Title
        title_label = ttk.Label(main_frame, text="Pharmacy Management System", 
                             font=("Helvetica", 16, "bold"))
        title_label.pack(pady=20)

        # Login frame
        login_frame = ttk.LabelFrame(main_frame, text="Admin Login", padding="20")
        login_frame.pack(expand=True, fill="both", padx=20, pady=10)

        # Username
        ttk.Label(login_frame, text="Username:").pack(fill="x", pady=5)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.pack(fill="x", pady=5)
        self.username_entry.focus()

        # Password
        ttk.Label(login_frame, text="Password:").pack(fill="x", pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.pack(fill="x", pady=5)

        # Login button
        login_button = ttk.Button(login_frame, text="Login", command=self.login)
        login_button.pack(pady=20)

        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())

        # Store the login status
        self.login_successful = False

    def login(self):
        """Validate admin credentials"""
        ADMIN_USERNAME = "b"
        ADMIN_PASSWORD = "b"

        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password")
            return

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            self.login_successful = True
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, tk.END)

    def run(self):
        """Run the login window"""
        self.root.mainloop()
        return self.login_successful