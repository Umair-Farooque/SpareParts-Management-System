import tkinter as tk
from tkinter import ttk, messagebox
from dashboard_window import DashboardWindow


class LoginWindow:
    def __init__(self, auth, inventory, sales, printer):
        self.auth = auth
        self.inventory = inventory
        self.sales = sales
        self.printer = printer

        self.win = tk.Tk()
        self.win.title("Login - Al-Hafiz Autos")
        self.win.geometry("600x550")
        self.win.configure(bg="#f5f7fa")

        self.style = ttk.Style(self.win)
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=("Segoe UI", 11), background="#f5f7fa")
        self.style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)
        self.style.map("TButton",
                       background=[('active', '#1a237e')],
                       foreground=[('active', 'white')])

        # Main frame with padding
        main_frame = ttk.Frame(self.win, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(main_frame, text="Welcome to Al-Hafiz Autos", font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))

        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W, pady=(0, 5))
        self.u = ttk.Entry(main_frame, font=("Segoe UI", 12))
        self.u.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(main_frame, text="Password:").pack(anchor=tk.W, pady=(0, 5))
        self.p = ttk.Entry(main_frame, font=("Segoe UI", 12), show="*")
        self.p.pack(fill=tk.X, pady=(0, 20))

        btn_login = ttk.Button(main_frame, text="Login", command=self.login)
        btn_login.pack(fill=tk.X, pady=5)

        btn_register = ttk.Button(main_frame, text="Register", command=self.register)
        btn_register.pack(fill=tk.X, pady=5)

        btn_reset = ttk.Button(main_frame, text="Reset Password", command=self.reset_pw)
        btn_reset.pack(fill=tk.X, pady=5)

        self.center_window(self.win)
        self.u.focus()
        self.win.mainloop()

    def center_window(self, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def login(self):
        username = self.u.get().strip()
        password = self.p.get()
        if self.auth.validate_login(username, password):
            self.win.destroy()
            DashboardWindow(self.auth, self.inventory, self.sales, self.printer, username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register(self):
        self._popup_form(
            title="Register New User",
            fields=[
                ("Username", False),
                ("Password", True),
                ("Security Question", False),
                ("Answer", False)
            ],
            submit_callback=self._handle_register
        )

    def reset_pw(self):
        self._popup_form(
            title="Reset Password",
            fields=[
                ("Username", False),
                ("Security Question", False),
                ("Answer", False),
                ("New Password", True)
            ],
            submit_callback=self._handle_reset_password
        )

    def _popup_form(self, title, fields, submit_callback):
        top = tk.Toplevel(self.win)
        top.title(title)
        top.geometry("400x350")
        top.configure(bg="#f5f7fa")
        self.center_window(top)

        style = ttk.Style(top)
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 11), background="#f5f7fa")
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)
        style.map("TButton",
                  background=[('active', '#1a237e')],
                  foreground=[('active', 'white')])

        frame = ttk.Frame(top, padding=20)
        frame.pack(expand=True, fill=tk.BOTH)

        entries = {}

        for label_text, is_password in fields:
            ttk.Label(frame, text=label_text + ":").pack(anchor=tk.W, pady=(5, 2))
            entry = ttk.Entry(frame, show="*" if is_password else None, font=("Segoe UI", 12))
            entry.pack(fill=tk.X, pady=(0, 10))
            entries[label_text] = entry

        def on_submit():
            data = {k: v.get().strip() for k, v in entries.items()}
            if any(not val for val in data.values()):
                messagebox.showwarning("Missing Data", "Please fill in all fields.")
                return
            submit_callback(data, top)

        ttk.Button(frame, text="Submit", command=on_submit).pack(pady=10, fill=tk.X)

    def _handle_register(self, data, window):
        ok = self.auth.register_user(
            data["Username"], data["Password"], data["Security Question"], data["Answer"]
        )
        messagebox.showinfo("Status", "Registration successful." if ok else "User already exists.")
        if ok:
            window.destroy()

    def _handle_reset_password(self, data, window):
        ok = self.auth.reset_password(
            data["Username"], data["Security Question"], data["Answer"], data["New Password"]
        )
        messagebox.showinfo("Status", "Password reset successfully." if ok else "Password reset failed.")
        if ok:
            window.destroy()
