import customtkinter as ctk


# Draws a styled header row inside the given parent widget. 'columns' is a
# list of (label_text, pixel_width) tuples — one entry per column. Used by
# the History and Log tabs to show column titles above their data lists.
def make_table_header(parent, columns):
    header = ctk.CTkFrame(parent, fg_color=("gray80", "gray25"))
    header.pack(fill="x", padx=15)
    for col_text, col_width in columns:
        ctk.CTkLabel(
            header, text=col_text, width=col_width,
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w",
        ).pack(side="left", padx=(8, 0), pady=7)


# Removes all child widgets from a frame. Used before re-drawing a
# scrollable list so the old rows are deleted before new ones are added.
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()
