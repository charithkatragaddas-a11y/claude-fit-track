import customtkinter as ctk

from db import Database


class LoginWindow(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("FitTrack")
        self.geometry("420x320")
        self.resizable(False, False)
        self.db = Database()
        self.user_id = None
        self.username = None
        self._build()
        self.after(0, self._center)

    def _center(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"420x320+{(sw - 420) // 2}+{(sh - 320) // 2}")

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(expand=True, fill="both", padx=40, pady=30)

        ctk.CTkLabel(
            outer, text="FitTrack",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            outer, text="Enter your username to continue",
            font=ctk.CTkFont(size=13),
            text_color="gray60",
        ).pack(pady=(0, 20))

        self.entry = ctk.CTkEntry(
            outer,
            placeholder_text="Username",
            width=280,
            height=40,
            font=ctk.CTkFont(size=14),
            justify="center",
        )
        self.entry.pack(pady=(0, 16))
        self.entry.bind("<Return>", lambda _: self._login())

        btn_row = ctk.CTkFrame(outer, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(
            btn_row, text="Log In", width=130, height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._login,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            btn_row, text="Sign Up", width=130, height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            text_color=("gray10", "gray90"),
            command=self._signup,
        ).pack(side="left")

        self.msg_label = ctk.CTkLabel(
            outer, text="",
            font=ctk.CTkFont(size=12),
            wraplength=320,
        )
        self.msg_label.pack(pady=(14, 0))

    def _login(self):
        username = self.entry.get().strip()
        if not username:
            self._show_msg("Please enter a username.", "#F44336")
            return
        username = username.upper()
        user = self.db.get_user(username)
        if user is None:
            self._show_msg("Username not found. Use Sign Up to create an account.", "#F44336")
            return
        self.user_id = user[0]
        self.username = user[1]
        self.destroy()

    def _signup(self):
        username = self.entry.get().strip()
        if not username:
            self._show_msg("Please enter a username.", "#F44336")
            return
        username = username.upper()
        if self.db.get_user(username):
            self._show_msg("Username already taken. Try logging in instead.", "#FF9800")
            return
        self.user_id = self.db.create_user(username)
        self.username = username
        self.destroy()

    def _show_msg(self, text: str, color: str):
        self.msg_label.configure(text=text, text_color=color)
