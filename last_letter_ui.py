import random
import time
import string
import keyboard
import pyautogui
import tkinter as tk

# =========================
# LOAD WORDS
# =========================
with open("words.txt", "r", encoding="utf-8") as f:
    WORDS = [w.strip().lower() for w in f if w.strip().isalpha()]

# =========================
# STATE
# =========================
prefix = ""
last_word = "-"
status = "Waiting for letters..."
last_key_time = 0
active_tab = "main"

SUBMIT_DELAY = 0.25
MAX_PREFIX_LEN = 4

# =========================
# ROOT
# =========================
root = tk.Tk()
root.title("Troojin Prefix Typer")
root.geometry("520x330")
root.resizable(False, False)
root.attributes("-topmost", True)
root.configure(bg="#0b1220")

# =========================
# TOP NAV BAR
# =========================
nav = tk.Frame(root, bg="#0b1220")
nav.pack(fill="x", padx=20, pady=(14, 6))

tab_font = ("Segoe UI", 11, "bold")

tab_main = tk.Label(nav, text="Main", font=tab_font, fg="#38bdf8", bg="#0b1220", cursor="hand2")
tab_words = tk.Label(nav, text="Words", font=tab_font, fg="#94a3b8", bg="#0b1220", cursor="hand2")

nav = tk.Frame(root, bg="#0b1220")
nav.pack(fill="x", padx=60, pady=(14, 6))  # ⬅ more inner margin

tab_main.pack(side="left", padx=(0, 0))
tab_words.pack(side="right", padx=(0, 0))


# =========================
# UNDERLINE CANVAS (FULL WIDTH)
# =========================
underline_canvas = tk.Canvas(
    root,
    height=10,
    bg="#0b1220",
    highlightthickness=0
)
underline_canvas.pack(fill="x", padx=20)

def rounded_rect(x1, y1, x2, y2, r, **kwargs):
    points = [
        x1+r, y1,
        x2-r, y1,
        x2, y1,
        x2, y1+r,
        x2, y2-r,
        x2, y2,
        x2-r, y2,
        x1+r, y2,
        x1, y2,
        x1, y2-r,
        x1, y1+r,
        x1, y1
    ]
    return underline_canvas.create_polygon(points, smooth=True, **kwargs)

indicator = rounded_rect(0, 3, 80, 7, 6, fill="#38bdf8")

# =========================
# CONTENT FRAMES
# =========================
content = tk.Frame(root, bg="#0b1220")
content.pack(expand=True, fill="both")

main_frame = tk.Frame(content, bg="#0b1220")
words_frame = tk.Frame(content, bg="#0b1220")

for f in (main_frame, words_frame):
    f.place(relx=0, rely=0, relwidth=1, relheight=1)

# =========================
# MAIN CONTENT
# =========================
tk.Label(
    main_frame,
    text="Troojin Prefix Typer",
    font=("Segoe UI", 15, "bold"),
    fg="#38bdf8",
    bg="#0b1220"
).pack(pady=(20, 16))

def label(parent, text, size, color):
    return tk.Label(parent, text=text, font=("Segoe UI", size), fg=color, bg="#0b1220")

prefix_label = label(main_frame, "PREFIX: — — —", 13, "white")
prefix_label.pack(pady=6)

word_label = label(main_frame, "TYPED: —", 13, "#e879f9")
word_label.pack(pady=6)

status_label = label(main_frame, "Waiting for letters…", 10, "#facc15")
status_label.pack(pady=10)

label(main_frame, "Type 1–4 letters • ESC to quit", 9, "#64748b").pack(side="bottom", pady=12)

# =========================
# WORDS CONTENT
# =========================
tk.Label(
    words_frame,
    text="Words",
    font=("Segoe UI", 15, "bold"),
    fg="#38bdf8",
    bg="#0b1220"
).pack(pady=(20, 10))

words_box = tk.Text(
    words_frame,
    height=10,
    bg="#020617",
    fg="#e5e7eb",
    insertbackground="white",
    relief="flat"
)
words_box.pack(fill="x", padx=24)
words_box.insert("1.0", "\n".join(WORDS))

def save_words():
    global WORDS
    lines = words_box.get("1.0", "end").splitlines()
    WORDS = [w.strip().lower() for w in lines if w.strip().isalpha()]
    with open("words.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(WORDS))
    status_label.config(text="Words updated ✔")

tk.Button(
    words_frame,
    text="Save",
    command=save_words,
    bg="#1e293b",
    fg="white",
    relief="flat",
    padx=12,
    pady=4
).pack(pady=10)

# =========================
# TAB + UNDERLINE LOGIC
# =========================
def move_indicator(widget, thick=False):
    x = widget.winfo_x()
    w = widget.winfo_width()
    h = 7 if thick else 4
    underline_canvas.coords(indicator, x, 5-h//2, x+w, 5+h//2)

def activate_tab(name):
    global active_tab
    active_tab = name

    if name == "main":
        main_frame.tkraise()
        tab_main.config(fg="#38bdf8")
        tab_words.config(fg="#94a3b8")
        move_indicator(tab_main)
    else:
        words_frame.tkraise()
        tab_words.config(fg="#38bdf8")
        tab_main.config(fg="#94a3b8")
        move_indicator(tab_words)

def hover_in(e):
    move_indicator(e.widget, thick=True)

def hover_out(e):
    move_indicator(tab_main if active_tab == "main" else tab_words)

tab_main.bind("<Button-1>", lambda e: activate_tab("main"))
tab_words.bind("<Button-1>", lambda e: activate_tab("words"))

tab_main.bind("<Enter>", hover_in)
tab_words.bind("<Enter>", hover_in)
tab_main.bind("<Leave>", hover_out)
tab_words.bind("<Leave>", hover_out)

root.after(50, lambda: move_indicator(tab_main))
activate_tab("main")

# =========================
# LOGIC LOOP
# =========================
def find_word(start):
    m = [w for w in WORDS if w.startswith(start)]
    return random.choice(m) if m else None

def update_ui():
    prefix_label.config(text=f"PREFIX: {prefix.upper()}" if prefix else "PREFIX: — — —")
    word_label.config(text=f"TYPED: {last_word}")
    status_label.config(text=status)

def loop():
    global prefix, last_word, status, last_key_time

    root.attributes("-topmost", True)

    if active_tab == "main":
        for key in string.ascii_lowercase:
            if keyboard.is_pressed(key):
                if len(prefix) < MAX_PREFIX_LEN:
                    prefix += key
                    status = "Building prefix..."
                    last_key_time = time.time()
                    update_ui()
                    time.sleep(0.12)

        if prefix and time.time() - last_key_time > SUBMIT_DELAY:
            status = "Searching..."
            update_ui()

            word = find_word(prefix)
            if word:
                status = "Typing..."
                typed = word[len(prefix):]
                last_word = typed if typed else "(empty)"
                update_ui()

                time.sleep(random.uniform(0.05, 0.12))
                if typed:
                    pyautogui.write(typed, interval=random.uniform(0.01, 0.04))
                    pyautogui.press("enter") # handles everything

            prefix = ""
            status = "Waiting for letters..."
            update_ui()
            time.sleep(0.3)

    if keyboard.is_pressed("esc"):
        root.destroy()
        return

    root.after(30, loop)

update_ui()
root.after(100, loop)
root.mainloop()
