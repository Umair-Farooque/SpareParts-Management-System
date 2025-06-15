import tkinter as tk
from tkinter import messagebox
from dashboard_window import DashboardWindow

class LoginWindow:
    def __init__(self, auth, inventory, sales, printer):
        self.auth = auth
        self.inventory = inventory
        self.sales = sales
        self.printer = printer

        self.win = tk.Tk()
        self.win.title("Login - Al-Hafiz Autos")
        self.win.geometry("400x300")
        self.center_window(self.win)

        tk.Label(self.win, text="Username").pack()
        self.u = tk.Entry(self.win)
        self.u.pack()

        tk.Label(self.win, text="Password").pack()
        self.p = tk.Entry(self.win, show="*")
        self.p.pack()

        tk.Button(self.win, text="Login", command=self.login).pack(pady=5)
        tk.Button(self.win, text="Register", command=self.register).pack(pady=2)
        tk.Button(self.win, text="Reset Password", command=self.reset_pw).pack()

        self.win.mainloop()

    def center_window(self, win):
        win.update_idletasks()
        width = 400
        height = 300
        x = win.winfo_screenwidth() // 2 - width // 2
        y = win.winfo_screenheight() // 2 - height // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

    def login(self):
        username = self.u.get()
        password = self.p.get()
        if self.auth.validate_login(username, password):
            self.win.destroy()
            DashboardWindow(self.auth, self.inventory, self.sales, self.printer, username)
        else:
            messagebox.showerror("Error", "Invalid login")

    def register(self):
        top = tk.Toplevel(self.win)
        top.title("Register New User")
        top.geometry("400x300")
        self.center_window(top)

        fields = {}

        def submit():
            username = fields["Username"].get()
            password = fields["Password"].get()
            question = fields["Security Question"].get()
            answer = fields["Answer"].get()

            ok = self.auth.register_user(username, password, question, answer)
            messagebox.showinfo("Status", "Registration successful" if ok else "User already exists")
            top.destroy()

        for lbl in ["Username", "Password", "Security Question", "Answer"]:
            tk.Label(top, text=lbl).pack()
            entry = tk.Entry(top, show="*" if lbl == "Password" else None)
            entry.pack()
            fields[lbl] = entry

        tk.Button(top, text="Submit", command=submit).pack(pady=5)

    def reset_pw(self):
        top = tk.Toplevel(self.win)
        top.title("Reset Password")
        top.geometry("400x300")
        self.center_window(top)

        fields = {}

        def submit():
            username = fields["Username"].get()
            question = fields["Security Question"].get()
            answer = fields["Answer"].get()
            new_password = fields["New Password"].get()

            ok = self.auth.reset_password(username, question, answer, new_password)
            messagebox.showinfo("Status", "Password Reset" if ok else "Reset Failed")
            top.destroy()

        for lbl in ["Username", "Security Question", "Answer", "New Password"]:
            tk.Label(top, text=lbl).pack()
            entry = tk.Entry(top, show="*" if "Password" in lbl else None)
            entry.pack()
            fields[lbl] = entry

        tk.Button(top, text="Submit", command=submit).pack(pady=5)
