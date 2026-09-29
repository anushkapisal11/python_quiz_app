import tkinter as tk
import json
import os
from tkinter import messagebox


# -----------------------------
# Settings
# -----------------------------

QUIZ_MINUTES = 60
FONT = "Segoe UI"

# Light theme colours
BG = "#F3F6FB"
CARD = "#FFFFFF"
PRIMARY = "#4F46E5"
PRIMARY_DARK = "#4338CA"
TEXT = "#1F2937"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
HOVER_BG = "#EEF2FF"

GREEN = "#16A34A"
GREEN_BG = "#DCFCE7"
GREEN_TEXT = "#166534"

RED = "#DC2626"
RED_BG = "#FEE2E2"
RED_TEXT = "#991B1B"

AMBER = "#D97706"
AMBER_BG = "#FEF3C7"

GREY = "#E5E7EB"
DISABLED_FG = "#9CA3AF"

TOPIC_COLORS = [
    "#4F46E5", "#0284C7", "#059669", "#D97706",
    "#DC2626", "#7C3AED", "#DB2777"
]


# -----------------------------
# Base Paths
# -----------------------------

base_path = os.path.dirname(os.path.abspath(__file__))
questions_path = os.path.join(base_path, "questions")

users_file = os.path.join(base_path, "users.json")
leaderboard_file = os.path.join(base_path, "leaderboard.json")


# -----------------------------
# JSON File Helpers
# -----------------------------

def load_json_file(filename):

    try:

        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)

    except (OSError, ValueError):

        return []


def save_json_file(filename, data):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# -----------------------------
# User Data
# -----------------------------

users = load_json_file(users_file)
leaderboard = load_json_file(leaderboard_file)

current_user = ""


# -----------------------------
# Load Questions
# -----------------------------

def load_questions(filename):

    file_path = os.path.join(
        questions_path,
        filename
    )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# -----------------------------
# Topics
# -----------------------------

TOPICS = [
    ("Data Types", "data_types.json", "Python Data Types Quiz"),
    ("Operators", "operators.json", "Python Operators Quiz"),
    ("Loops", "loops.json", "Python Loops Quiz"),
    ("Strings", "strings.json", "Python Strings Quiz"),
    ("If-Else", "if_else.json", "Python If-Else Quiz"),
    ("Functions", "functions.json", "Python Functions Quiz"),
    ("Lists", "lists.json", "Python Lists Quiz"),
    ("Tuples", "tuples.json", "Python Tuples Quiz"),
    ("Sets", "sets.json", "Python Sets Quiz"),
    ("Dictionary", "dictionary.json", "Python Dictionary Quiz"),
    (
        "Lambda / Map / Filter / Reduce",
        "lambda_map_filter_reduce.json",
        "Python Lambda / Map / Filter / Reduce Quiz"
    ),
    (
        "Exception Handling",
        "exception_handling.json",
        "Python Exception Handling Quiz"
    ),
    (
        "File Handling",
        "file_handling.json",
        "Python File Handling Quiz"
    ),
    ("OOP", "oops.json", "Python OOP Quiz"),
    (
        "Inheritance",
        "inheritance.json",
        "Python Inheritance Quiz"
    ),
    (
        "Polymorphism",
        "polymorphism.json",
        "Python Polymorphism Quiz"
    ),
    (
        "Encapsulation",
        "encapsulation.json",
        "Python Encapsulation Quiz"
    ),
    (
        "Abstraction",
        "abstraction.json",
        "Python Abstraction Quiz"
    ),
    (
        "Decorators",
        "decorator.json",
        "Python Decorators Quiz"
    ),
    (
        "Generators",
        "generators.json",
        "Python Generators Quiz"
    ),
    (
        "Modules & Packages",
        "modules_packages.json",
        "Python Modules & Packages Quiz"
    ),
]


all_questions = {}
load_problems = []


for _, filename, _ in TOPICS:

    try:

        loaded = load_questions(filename)

    except (OSError, ValueError) as error:

        load_problems.append(
            f"{filename}: could not be loaded ({error})"
        )

        loaded = []

    valid_questions = []

    for number, item in enumerate(
        loaded,
        start=1
    ):

        if not all(
            key in item
            for key in (
                "question",
                "options",
                "answer"
            )
        ):

            load_problems.append(
                f"{filename}: question {number} "
                "is missing a field"
            )

            continue

        if item["answer"] not in item["options"]:

            load_problems.append(
                f"{filename}: question {number} - "
                "answer is not in options"
            )

        valid_questions.append(item)

    all_questions[filename] = valid_questions


# -----------------------------
# Main Window
# -----------------------------

root = tk.Tk()

root.title("Python Timer Quiz")
root.configure(bg=BG)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_width = min(
    1100,
    screen_width - 60
)

window_height = min(
    720,
    screen_height - 100
)

window_x = (
    screen_width -
    window_width
) // 2

window_y = max(
    (
        screen_height -
        window_height
    ) // 2 - 20,
    0
)

root.geometry(
    f"{window_width}x{window_height}+"
    f"{window_x}+{window_y}"
)

root.minsize(
    900,
    600
)


# -----------------------------
# Global Variables
# -----------------------------

current_question = 0
time_left = QUIZ_MINUTES * 60

user_answers = []
quiz_questions = []
current_quiz_title = ""

timer_job = None
active_canvas = None
ui = {}


# -----------------------------
# Small Helpers
# -----------------------------

def shade(color, factor):

    color = color.lstrip("#")

    red = int(
        color[0:2],
        16
    )

    green = int(
        color[2:4],
        16
    )

    blue = int(
        color[4:6],
        16
    )

    red = max(
        0,
        min(
            255,
            int(red * factor)
        )
    )

    green = max(
        0,
        min(
            255,
            int(green * factor)
        )
    )

    blue = max(
        0,
        min(
            255,
            int(blue * factor)
        )
    )

    return (
        f"#{red:02x}"
        f"{green:02x}"
        f"{blue:02x}"
    )


def make_button(
    parent,
    text,
    command,
    bg=PRIMARY,
    fg="white",
    hover=PRIMARY_DARK,
    font_size=12,
    padx=22,
    pady=9
):

    button = tk.Label(
        parent,
        text=text,
        bg=bg,
        fg=fg,
        font=(
            FONT,
            font_size,
            "bold"
        ),
        padx=padx,
        pady=pady,
        cursor="hand2"
    )

    button.command = command
    button.enabled = True
    button.normal_bg = bg
    button.normal_fg = fg
    button.hover_bg = hover

    def on_enter(event):

        if button.enabled:

            button.config(
                bg=button.hover_bg
            )

    def on_leave(event):

        if button.enabled:

            button.config(
                bg=button.normal_bg
            )

    def on_click(event):

        if button.enabled:

            button.command()

    button.bind(
        "<Enter>",
        on_enter
    )

    button.bind(
        "<Leave>",
        on_leave
    )

    button.bind(
        "<Button-1>",
        on_click
    )

    return button


def set_button_enabled(
    button,
    enabled
):

    button.enabled = enabled

    if enabled:

        button.config(
            bg=button.normal_bg,
            fg=button.normal_fg,
            cursor="hand2"
        )

    else:

        button.config(
            bg=GREY,
            fg=DISABLED_FG,
            cursor="arrow"
        )


def restyle_button(
    button,
    text,
    bg,
    hover,
    fg="white"
):

    button.normal_bg = bg
    button.normal_fg = fg
    button.hover_bg = hover

    button.config(
        text=text
    )

    set_button_enabled(
        button,
        button.enabled
    )


def make_stat_card(
    parent,
    value,
    label,
    color=PRIMARY
):

    card = tk.Frame(
        parent,
        bg=CARD,
        highlightthickness=1,
        highlightbackground=BORDER
    )

    tk.Label(
        card,
        text=value,
        font=(
            FONT,
            22,
            "bold"
        ),
        bg=CARD,
        fg=color
    ).pack(
        padx=26,
        pady=(12, 0)
    )

    tk.Label(
        card,
        text=label,
        font=(
            FONT,
            10
        ),
        bg=CARD,
        fg=MUTED
    ).pack(
        padx=26,
        pady=(0, 12)
    )

    return card


def make_header(
    title,
    subtitle=None
):

    header = tk.Frame(
        root,
        bg=PRIMARY
    )

    header.pack(
        fill="x"
    )

    text_frame = tk.Frame(
        header,
        bg=PRIMARY
    )

    text_frame.pack(
        side="left",
        padx=25,
        pady=14
    )

    tk.Label(
        text_frame,
        text=title,
        font=(
            FONT,
            20,
            "bold"
        ),
        bg=PRIMARY,
        fg="white"
    ).pack(
        anchor="w"
    )

    if subtitle:

        tk.Label(
            text_frame,
            text=subtitle,
            font=(
                FONT,
                11
            ),
            bg=PRIMARY,
            fg="#C7D2FE"
        ).pack(
            anchor="w"
        )

    return header


def header_button(
    header,
    text,
    command
):

    button = make_button(
        header,
        text,
        command,
        bg="white",
        fg=PRIMARY,
        hover=HOVER_BG,
        font_size=11,
        padx=18,
        pady=7
    )

    button.pack(
        side="right",
        padx=(0, 20)
    )

    return button


# -----------------------------
# Mouse Wheel
# -----------------------------

def on_mouse_wheel(event):

    if active_canvas is None:
        return

    if event.num == 4:

        step = -1

    elif event.num == 5:

        step = 1

    else:

        step = int(
            -1 * (
                event.delta / 120
            )
        )

        if step == 0:

            step = (
                -1
                if event.delta > 0
                else 1
            )

    try:

        active_canvas.yview_scroll(
            step,
            "units"
        )

    except tk.TclError:

        pass


root.bind_all(
    "<MouseWheel>",
    on_mouse_wheel
)

root.bind_all(
    "<Button-4>",
    on_mouse_wheel
)

root.bind_all(
    "<Button-5>",
    on_mouse_wheel
)


def make_scrollable(
    parent,
    bg=BG
):

    global active_canvas

    container = tk.Frame(
        parent,
        bg=bg
    )

    canvas = tk.Canvas(
        container,
        bg=bg,
        highlightthickness=0,
        yscrollincrement=40
    )

    bar = tk.Scrollbar(
        container,
        orient="vertical",
        command=canvas.yview
    )

    inner = tk.Frame(
        canvas,
        bg=bg
    )

    window_id = canvas.create_window(
        (0, 0),
        window=inner,
        anchor="nw"
    )

    inner.bind(
        "<Configure>",
        lambda e:
        canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.bind(
        "<Configure>",
        lambda e:
        canvas.itemconfigure(
            window_id,
            width=e.width
        )
    )

    canvas.configure(
        yscrollcommand=bar.set
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    bar.pack(
        side="right",
        fill="y"
    )

    active_canvas = canvas

    return (
        container,
        canvas,
        inner
    )


# -----------------------------
# Clear Window
# -----------------------------

def clear_window():

    global timer_job
    global active_canvas
    global ui

    if timer_job is not None:

        try:

            root.after_cancel(
                timer_job
            )

        except tk.TclError:

            pass

        timer_job = None

    active_canvas = None
    ui = {}

    for sequence in (
        "<Left>",
        "<Right>",
        "<Key-1>",
        "<Key-2>",
        "<Key-3>",
        "<Key-4>"
    ):

        root.unbind(sequence)

    for widget in root.winfo_children():

        widget.destroy()


# ============================================================
# REGISTRATION
# ============================================================

def show_registration():

    clear_window()

    wrapper = tk.Frame(
        root,
        bg=BG
    )

    wrapper.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )

    tk.Label(
        wrapper,
        text="Create Account",
        font=(
            FONT,
            30,
            "bold"
        ),
        bg=BG,
        fg=PRIMARY
    ).pack()

    tk.Label(
        wrapper,
        text="Register before taking the quiz",
        font=(
            FONT,
            12
        ),
        bg=BG,
        fg=MUTED
    ).pack(
        pady=(5, 25)
    )

    card = tk.Frame(
        wrapper,
        bg=CARD,
        highlightthickness=1,
        highlightbackground=BORDER
    )

    card.pack(
        padx=20,
        pady=10
    )

    tk.Label(
        card,
        text="Full Name",
        font=(
            FONT,
            11,
            "bold"
        ),
        bg=CARD,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=30,
        pady=(25, 5)
    )

    name_entry = tk.Entry(
        card,
        font=(
            FONT,
            12
        ),
        width=30,
        relief="solid",
        bd=1
    )

    name_entry.pack(
        padx=30,
        ipady=8
    )

    tk.Label(
        card,
        text="Username",
        font=(
            FONT,
            11,
            "bold"
        ),
        bg=CARD,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=30,
        pady=(15, 5)
    )

    username_entry = tk.Entry(
        card,
        font=(
            FONT,
            12
        ),
        width=30,
        relief="solid",
        bd=1
    )

    username_entry.pack(
        padx=30,
        ipady=8
    )

    tk.Label(
        card,
        text="Password",
        font=(
            FONT,
            11,
            "bold"
        ),
        bg=CARD,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=30,
        pady=(15, 5)
    )

    password_entry = tk.Entry(
        card,
        font=(
            FONT,
            12
        ),
        width=30,
        show="*",
        relief="solid",
        bd=1
    )

    password_entry.pack(
        padx=30,
        ipady=8
    )

    tk.Label(
        card,
        text="Confirm Password",
        font=(
            FONT,
            11,
            "bold"
        ),
        bg=CARD,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=30,
        pady=(15, 5)
    )

    confirm_entry = tk.Entry(
        card,
        font=(
            FONT,
            12
        ),
        width=30,
        show="*",
        relief="solid",
        bd=1
    )

    confirm_entry.pack(
        padx=30,
        ipady=8
    )

    def register_user():

        name = name_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get()
        confirm = confirm_entry.get()

        if not name or not username or not password:

            messagebox.showwarning(
                "Registration",
                "Please fill all fields."
            )

            return

        if password != confirm:

            messagebox.showerror(
                "Registration",
                "Passwords do not match."
            )

            return

        for user in users:

            if user["username"].lower() == username.lower():

                messagebox.showerror(
                    "Registration",
                    "Username already exists."
                )

                return

        users.append(
            {
                "name": name,
                "username": username,
                "password": password
            }
        )

        save_json_file(
            users_file,
            users
        )

        messagebox.showinfo(
            "Registration Successful",
            "Account created successfully!\n"
            "You can now login."
        )

        show_login()

    make_button(
        card,
        "Register",
        register_user,
        font_size=13,
        padx=45,
        pady=11
    ).pack(
        pady=(25, 10)
    )

    make_button(
        card,
        "Already have an account? Login",
        show_login,
        bg=HOVER_BG,
        fg=PRIMARY,
        hover="#E0E7FF",
        font_size=10,
        padx=18,
        pady=8
    ).pack(
        pady=(0, 25)
    )

    name_entry.focus()


# ============================================================
# LOGIN
# ============================================================

def show_login():

    clear_window()

    wrapper = tk.Frame(
        root,
        bg=BG
    )

    wrapper.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )

    tk.Label(
        wrapper,
        text="Welcome Back",
        font=(
            FONT,
            30,
            "bold"
        ),
        bg=BG,
        fg=PRIMARY
    ).pack()

    tk.Label(
        wrapper,
        text="Login to continue your quiz",
        font=(
            FONT,
            12
        ),
        bg=BG,
        fg=MUTED
    ).pack(
        pady=(5, 25)
    )

    card = tk.Frame(
        wrapper,
        bg=CARD,
        highlightthickness=1,
        highlightbackground=BORDER
    )

    card.pack(
        padx=20
    )

    tk.Label(
        card,
        text="Username",
        font=(
            FONT,
            11,
            "bold"
        ),
        bg=CARD,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=30,
        pady=(30, 5)
    )

    username_entry = tk.Entry(
        card,
        font=(
            FONT,
            12
        ),
        width=30,
        relief="solid",
        bd=1
    )

    username_entry.pack(
        padx=30,
        ipady=8
    )

    tk.Label(
        card,
        text="Password",
        font=(
            FONT,
            11,
            "bold"
        ),
        bg=CARD,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=30,
        pady=(15, 5)
    )

    password_entry = tk.Entry(
        card,
        font=(
            FONT,
            12
        ),
        width=30,
        show="*",
        relief="solid",
        bd=1
    )

    password_entry.pack(
        padx=30,
        ipady=8
    )

    def login_user():

        global current_user

        username = username_entry.get().strip()
        password = password_entry.get()

        if not username or not password:

            messagebox.showwarning(
                "Login",
                "Please enter username and password."
            )

            return

        for user in users:

            if (
                user["username"].lower()
                == username.lower()
                and user["password"] == password
            ):

                current_user = user["name"]

                messagebox.showinfo(
                    "Login Successful",
                    f"Welcome, {current_user}!"
                )

                show_home()

                return

        messagebox.showerror(
            "Login Failed",
            "Invalid username or password."
        )

    make_button(
        card,
        "Login",
        login_user,
        font_size=13,
        padx=50,
        pady=11
    ).pack(
        pady=(25, 10)
    )

    make_button(
        card,
        "Create New Account",
        show_registration,
        bg=HOVER_BG,
        fg=PRIMARY,
        hover="#E0E7FF",
        font_size=10,
        padx=20,
        pady=8
    ).pack(
        pady=(0, 30)
    )

    username_entry.focus()


# ============================================================
# HOME SCREEN
# ============================================================

def show_home():

    clear_window()

    wrapper = tk.Frame(
        root,
        bg=BG
    )

    wrapper.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )

    tk.Label(
        wrapper,
        text="Python Timer Quiz",
        font=(
            FONT,
            40,
            "bold"
        ),
        bg=BG,
        fg=PRIMARY
    ).pack()

    tk.Label(
        wrapper,
        text=f"Welcome, {current_user}",
        font=(
            FONT,
            16,
            "bold"
        ),
        bg=BG,
        fg=TEXT
    ).pack(
        pady=(5, 3)
    )

    tk.Label(
        wrapper,
        text="Topic-wise Python practice with a timer",
        font=(
            FONT,
            14
        ),
        bg=BG,
        fg=MUTED
    ).pack(
        pady=(0, 25)
    )

    stats = tk.Frame(
        wrapper,
        bg=BG
    )

    stats.pack(
        pady=10
    )

    total_questions = sum(
        len(items)
        for items in all_questions.values()
    )

    stat_items = [
        (
            str(len(TOPICS)),
            "Topics"
        ),
        (
            str(total_questions),
            "Questions"
        ),
        (
            f"{QUIZ_MINUTES} min",
            "Time per quiz"
        )
    ]

    for value, label in stat_items:

        make_stat_card(
            stats,
            value,
            label
        ).pack(
            side="left",
            padx=10
        )

    buttons = tk.Frame(
        wrapper,
        bg=BG
    )

    buttons.pack(
        pady=(30, 0)
    )

    make_button(
        buttons,
        "Start Quiz",
        show_topics,
        font_size=15,
        padx=45,
        pady=13
    ).pack(
        side="left",
        padx=6
    )

    make_button(
        buttons,
        "Leaderboard",
        show_leaderboard,
        bg="#0284C7",
        hover=shade(
            "#0284C7",
            0.85
        ),
        font_size=15,
        padx=35,
        pady=13
    ).pack(
        side="left",
        padx=6
    )

    make_button(
        buttons,
        "Logout",
        show_login,
        bg=HOVER_BG,
        fg=PRIMARY,
        hover="#E0E7FF",
        font_size=15,
        padx=35,
        pady=13
    ).pack(
        side="left",
        padx=6
    )


# ============================================================
# TOPIC SELECTION
# ============================================================

def make_topic_card(
    parent,
    title,
    subtitle,
    color,
    command
):

    hover_color = shade(
        color,
        0.85
    )

    card = tk.Frame(
        parent,
        bg=color
    )

    name = tk.Label(
        card,
        text=title,
        font=(
            FONT,
            14,
            "bold"
        ),
        bg=color,
        fg="white",
        wraplength=240,
        justify="left",
        anchor="w"
    )

    name.pack(
        fill="x",
        padx=18,
        pady=(18, 2)
    )

    info = tk.Label(
        card,
        text=subtitle,
        font=(
            FONT,
            10
        ),
        bg=color,
        fg="white",
        anchor="w"
    )

    info.pack(
        fill="x",
        padx=18,
        pady=(0, 18)
    )

    parts = (
        card,
        name,
        info
    )

    def on_enter(event):

        for part in parts:

            part.config(
                bg=hover_color
            )

    def on_leave(event):

        for part in parts:

            part.config(
                bg=color
            )

    def on_click(event):

        command()

    for part in parts:

        part.config(
            cursor="hand2"
        )

        part.bind(
            "<Enter>",
            on_enter
        )

        part.bind(
            "<Leave>",
            on_leave
        )

        part.bind(
            "<Button-1>",
            on_click
        )

    return card


def show_topics():

    clear_window()

    header = make_header(
        "Select a Topic",
        f"User: {current_user}"
    )

    header_button(
        header,
        "Leaderboard",
        show_leaderboard
    )

    header_button(
        header,
        "Back",
        show_home
    )

    container, canvas, inner = make_scrollable(
        root
    )

    container.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=15
    )

    columns = 3

    for column in range(columns):

        inner.columnconfigure(
            column,
            weight=1,
            uniform="topic"
        )

    for index, (
        topic_name,
        filename,
        quiz_title
    ) in enumerate(TOPICS):

        color = TOPIC_COLORS[
            index %
            len(TOPIC_COLORS)
        ]

        questions = all_questions[
            filename
        ]

        card = make_topic_card(
            inner,
            f"{index + 1}. {topic_name}",
            f"{len(questions)} questions",
            color,
            lambda q=questions,
                   t=quiz_title:
                   start_quiz(q, t)
        )

        card.grid(
            row=index // columns,
            column=index % columns,
            padx=8,
            pady=8,
            sticky="nsew"
        )


# ============================================================
# START QUIZ
# ============================================================

def start_quiz(
    questions,
    quiz_title
):

    global current_question
    global time_left
    global user_answers
    global quiz_questions
    global current_quiz_title
    global timer_job

    if not questions:

        messagebox.showinfo(
            "No Questions",
            "This topic does not have any questions yet."
        )

        return

    quiz_questions = questions

    current_quiz_title = quiz_title

    current_question = 0

    time_left = (
        QUIZ_MINUTES * 60
    )

    user_answers = [
        ""
        for _ in range(
            len(quiz_questions)
        )
    ]

    show_quiz()

    update_timer_display()

    timer_job = root.after(
        1000,
        tick
    )


# ============================================================
# TIMER
# ============================================================

def tick():

    global time_left
    global timer_job

    time_left -= 1

    update_timer_display()

    if time_left <= 0:

        timer_job = None

        show_result()

    else:

        timer_job = root.after(
            1000,
            tick
        )


def update_timer_display():

    label = ui.get(
        "timer"
    )

    if label is None:
        return

    minutes, seconds = divmod(
        max(
            time_left,
            0
        ),
        60
    )

    if time_left <= 120:

        color = RED

    elif time_left <= 600:

        color = AMBER

    else:

        color = GREEN

    label.config(
        text=(
            f"Time Left  "
            f"{minutes:02d}:{seconds:02d}"
        ),
        fg=color
    )


# ============================================================
# QUIZ SCREEN
# ============================================================

def show_quiz():

    clear_window()

    header = tk.Frame(
        root,
        bg=PRIMARY
    )

    header.pack(
        fill="x"
    )

    tk.Label(
        header,
        text=current_quiz_title,
        font=(
            FONT,
            18,
            "bold"
        ),
        bg=PRIMARY,
        fg="white"
    ).pack(
        side="left",
        padx=25,
        pady=14
    )

    quit_button = make_button(
        header,
        "Quit Quiz",
        quit_quiz,
        bg="white",
        fg=RED,
        hover=RED_BG,
        font_size=11,
        padx=16,
        pady=7
    )

    quit_button.pack(
        side="right",
        padx=(0, 20)
    )

    ui["timer"] = tk.Label(
        header,
        text="",
        font=(
            FONT,
            13,
            "bold"
        ),
        bg="white",
        fg=GREEN,
        padx=14,
        pady=6
    )

    ui["timer"].pack(
        side="right",
        padx=15
    )

    progress = tk.Frame(
        root,
        bg=BG
    )

    progress.pack(
        fill="x",
        padx=25,
        pady=(12, 0)
    )

    ui["progress_text"] = tk.Label(
        progress,
        text="",
        font=(
            FONT,
            11,
            "bold"
        ),
        bg=BG,
        fg=TEXT,
        anchor="w"
    )

    ui["progress_text"].pack(
        fill="x"
    )

    trough = tk.Frame(
        progress,
        bg=GREY,
        height=10
    )

    trough.pack(
        fill="x",
        pady=(6, 0)
    )

    ui["bar"] = tk.Frame(
        trough,
        bg=PRIMARY
    )

    ui["bar"].place(
        x=0,
        y=0,
        relheight=1,
        relwidth=0
    )

    body = tk.Frame(
        root,
        bg=BG
    )

    body.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=15
    )

    body.columnconfigure(
        0,
        weight=1
    )

    body.rowconfigure(
        0,
        weight=1
    )

    card = tk.Frame(
        body,
        bg=CARD,
        highlightthickness=1,
        highlightbackground=BORDER
    )

    card.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, 15)
    )

    panel = tk.Frame(
        body,
        bg=CARD,
        width=290,
        highlightthickness=1,
        highlightbackground=BORDER
    )

    panel.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    panel.pack_propagate(
        False
    )

    nav = tk.Frame(
        card,
        bg=CARD
    )

    nav.pack(
        side="bottom",
        fill="x",
        padx=28,
        pady=20
    )

    ui["prev_btn"] = make_button(
        nav,
        "Previous",
        go_previous,
        bg=HOVER_BG,
        fg=PRIMARY,
        hover="#E0E7FF"
    )

    ui["prev_btn"].pack(
        side="left"
    )

    ui["next_btn"] = make_button(
        nav,
        "Next",
        go_next
    )

    ui["next_btn"].pack(
        side="right"
    )

    ui["q_number"] = tk.Label(
        card,
        text="",
        font=(
            FONT,
            11,
            "bold"
        ),
        bg=CARD,
        fg=PRIMARY,
        anchor="w"
    )

    ui["q_number"].pack(
        fill="x",
        padx=28,
        pady=(22, 4)
    )

    ui["q_text"] = tk.Label(
        card,
        text="",
        font=(
            FONT,
            16,
            "bold"
        ),
        bg=CARD,
        fg=TEXT,
        anchor="w",
        justify="left",
        wraplength=640
    )

    ui["q_text"].pack(
        fill="x",
        padx=28,
        pady=(0, 16)
    )

    ui["options_frame"] = tk.Frame(
        card,
        bg=CARD
    )

    ui["options_frame"].pack(
        fill="x",
        padx=28
    )

    ui["feedback"] = tk.Label(
        card,
        text="",
        font=(
            FONT,
            12,
            "bold"
        ),
        bg=CARD,
        fg=MUTED,
        anchor="w",
        justify="left",
        wraplength=640
    )

    ui["feedback"].pack(
        fill="x",
        padx=28,
        pady=(12, 0)
    )

    ui["option_labels"] = []
    ui["wrap"] = 620

    card.bind(
        "<Configure>",
        on_card_resize
    )

    tk.Label(
        panel,
        text="Questions",
        font=(
            FONT,
            13,
            "bold"
        ),
        bg=CARD,
        fg=TEXT,
        anchor="w"
    ).pack(
        fill="x",
        padx=16,
        pady=(16, 8)
    )

    legend = tk.Frame(
        panel,
        bg=CARD
    )

    legend.pack(
        side="bottom",
        fill="x",
        padx=16,
        pady=(6, 14)
    )

    legend_items = [
        (
            GREEN,
            "Correct",
            False
        ),
        (
            RED,
            "Wrong",
            False
        ),
        (
            GREY,
            "Not answered",
            False
        ),
        (
            "white",
            "Current",
            True
        )
    ]

    for index, (
        color,
        text,
        outlined
    ) in enumerate(
        legend_items
    ):

        item = tk.Frame(
            legend,
            bg=CARD
        )

        item.grid(
            row=index // 2,
            column=index % 2,
            sticky="w",
            padx=(0, 12),
            pady=2
        )

        tk.Frame(
            item,
            bg=color,
            width=12,
            height=12,
            highlightthickness=(
                2
                if outlined
                else 0
            ),
            highlightbackground=TEXT
        ).pack(
            side="left"
        )

        tk.Label(
            item,
            text=text,
            font=(
                FONT,
                9
            ),
            bg=CARD,
            fg=MUTED
        ).pack(
            side="left",
            padx=5
        )

    (
        palette_container,
        palette_canvas,
        palette_inner
    ) = make_scrollable(
        panel,
        bg=CARD
    )

    palette_container.pack(
        fill="both",
        expand=True,
        padx=(12, 4),
        pady=(0, 4)
    )

    ui["palette"] = []

    columns = 5

    for index in range(
        len(quiz_questions)
    ):

        cell = tk.Label(
            palette_inner,
            text=str(index + 1),
            width=3,
            font=(
                FONT,
                10,
                "bold"
            ),
            padx=4,
            pady=3,
            cursor="hand2",
            highlightthickness=2
        )

        cell.grid(
            row=index // columns,
            column=index % columns,
            padx=2,
            pady=2
        )

        cell.bind(
            "<Button-1>",
            lambda e, n=index:
            goto_question(n)
        )

        ui["palette"].append(
            cell
        )

    root.bind(
        "<Left>",
        lambda e:
        goto_question(
            current_question - 1
        )
    )

    root.bind(
        "<Right>",
        lambda e:
        goto_question(
            current_question + 1
        )
    )

    for number in range(1, 5):

        root.bind(
            f"<Key-{number}>",
            lambda e, n=number:
            choose_by_number(n)
        )

    render_question()


# ============================================================
# RESIZE QUESTION CARD
# ============================================================

def on_card_resize(event):

    if "q_text" not in ui:
        return

    wrap = max(
        event.width - 120,
        300
    )

    ui["wrap"] = wrap

    ui["q_text"].config(
        wraplength=max(
            event.width - 60,
            300
        )
    )

    ui["feedback"].config(
        wraplength=max(
            event.width - 60,
            300
        )
    )

    for label, _ in ui["option_labels"]:

        label.config(
            wraplength=wrap
        )


# ============================================================
# RENDER QUESTION
# ============================================================

def render_question():

    question = quiz_questions[
        current_question
    ]

    ui["q_number"].config(
        text=(
            f"Question "
            f"{current_question + 1} "
            f"of "
            f"{len(quiz_questions)}"
        )
    )

    ui["q_text"].config(
        text=question["question"]
    )

    for widget in ui[
        "options_frame"
    ].winfo_children():

        widget.destroy()

    ui["option_labels"] = []

    for index, option in enumerate(
        question["options"]
    ):

        label = tk.Label(
            ui["options_frame"],
            text=(
                f"{chr(65 + index)}.   "
                f"{option}"
            ),
            font=(
                FONT,
                13
            ),
            bg=CARD,
            fg=TEXT,
            anchor="w",
            justify="left",
            wraplength=ui["wrap"],
            padx=16,
            pady=11,
            highlightthickness=2,
            highlightbackground=BORDER,
            cursor="hand2"
        )

        label.pack(
            fill="x",
            pady=5
        )

        label.bind(
            "<Enter>",
            lambda e, l=label:
            hover_option(
                l,
                True
            )
        )

        label.bind(
            "<Leave>",
            lambda e, l=label:
            hover_option(
                l,
                False
            )
        )

        label.bind(
            "<Button-1>",
            lambda e, o=option:
            select_answer(o)
        )

        ui["option_labels"].append(
            (
                label,
                option
            )
        )

    style_options()
    update_feedback()
    update_nav()
    refresh_palette()
    refresh_progress()


# ============================================================
# HOVER OPTION
# ============================================================

def hover_option(
    label,
    entering
):

    if entering:

        selected = user_answers[
            current_question
        ]

        selected_text = label.cget(
            "text"
        ).split(
            ".   ",
            1
        )[-1]

        if selected_text == selected:

            return

        label.config(
            bg=HOVER_BG,
            highlightbackground=PRIMARY
        )

    else:

        style_options()


# ============================================================
# STYLE OPTIONS
# ============================================================

def style_options():

    chosen = user_answers[
        current_question
    ]

    for label, option in ui[
        "option_labels"
    ]:

        if option == chosen:

            label.config(
                bg=HOVER_BG,
                fg=PRIMARY,
                highlightbackground=PRIMARY,
                cursor="hand2"
            )

        else:

            label.config(
                bg=CARD,
                fg=TEXT,
                highlightbackground=BORDER,
                cursor="hand2"
            )


# ============================================================
# FEEDBACK
# ============================================================

def update_feedback():

    chosen = user_answers[
        current_question
    ]

    if chosen == "":

        ui["feedback"].config(
            text=(
                "Choose an option. "
                "You can change your answer anytime."
            ),
            fg=MUTED
        )

    else:

        ui["feedback"].config(
            text=(
                "Answer selected. "
                "You can change it before submitting."
            ),
            fg=PRIMARY
        )


# ============================================================
# NAVIGATION
# ============================================================

def update_nav():

    is_first = (
        current_question == 0
    )

    is_last = (
        current_question ==
        len(quiz_questions) - 1
    )

    set_button_enabled(
        ui["prev_btn"],
        not is_first
    )

    if is_last:

        restyle_button(
            ui["next_btn"],
            "Submit",
            GREEN,
            shade(
                GREEN,
                0.85
            )
        )

    else:

        restyle_button(
            ui["next_btn"],
            "Next",
            PRIMARY,
            PRIMARY_DARK
        )


# ============================================================
# PROGRESS
# ============================================================

def refresh_progress():

    total = len(
        quiz_questions
    )

    answered = 0

    for answer in user_answers:

        if answer != "":

            answered += 1

    ui["progress_text"].config(
        text=(
            f"Answered "
            f"{answered} / {total}"
        )
    )

    ui["bar"].place_configure(
        relwidth=(
            answered / total
            if total
            else 0
        )
    )


# ============================================================
# QUESTION PALETTE
# ============================================================

def refresh_palette():

    for index, cell in enumerate(
        ui["palette"]
    ):

        answer = user_answers[
            index
        ]

        if answer == "":

            bg = GREY
            fg = TEXT

        else:

            bg = HOVER_BG
            fg = PRIMARY

        if index == current_question:

            border = TEXT

        else:

            border = bg

        cell.config(
            bg=bg,
            fg=fg,
            highlightbackground=border,
            highlightcolor=border
        )


# ============================================================
# ANSWER / NAVIGATION
# ============================================================

def select_answer(option):

    # User can change answer anytime.
    # Correct/Wrong is checked only after Submit.

    user_answers[
        current_question
    ] = option

    style_options()

    update_feedback()

    refresh_palette()

    refresh_progress()


def choose_by_number(number):

    options = quiz_questions[
        current_question
    ]["options"]

    if number <= len(options):

        select_answer(
            options[
                number - 1
            ]
        )


def goto_question(index):

    global current_question

    if 0 <= index < len(
        quiz_questions
    ):

        current_question = index

        render_question()


def go_previous():

    goto_question(
        current_question - 1
    )


def go_next():

    if current_question < (
        len(quiz_questions) - 1
    ):

        goto_question(
            current_question + 1
        )

    else:

        submit_quiz()


# ============================================================
# SUBMIT QUIZ
# ============================================================

def submit_quiz():

    unanswered = user_answers.count(
        ""
    )

    if unanswered:

        proceed = messagebox.askyesno(
            "Submit Quiz",
            f"You have {unanswered} "
            "unanswered question(s).\n"
            "Do you want to submit anyway?"
        )

        if not proceed:

            return

    show_result()


# ============================================================
# QUIT QUIZ
# ============================================================

def quit_quiz():

    answer = messagebox.askyesno(
        "Quit Quiz",
        "Are you sure you want to quit the quiz?"
    )

    if answer:

        show_topics()


# ============================================================
# SAVE LEADERBOARD
# ============================================================

def save_score(
    total,
    correct,
    wrong,
    unattempted,
    percentage,
    time_taken
):

    global leaderboard

    leaderboard.append(
        {
            "name": current_user,
            "topic": current_quiz_title,
            "score": correct,
            "total": total,
            "percentage": round(
                percentage,
                1
            ),
            "wrong": wrong,
            "unattempted": unattempted,
            "time": time_taken
        }
    )

    save_json_file(
        leaderboard_file,
        leaderboard
    )


# ============================================================
# RESULT SCREEN
# ============================================================

def show_result():

    elapsed = (
        QUIZ_MINUTES * 60
        - max(
            time_left,
            0
        )
    )

    clear_window()

    correct = 0
    wrong = 0
    unattempted = 0

    for index, question in enumerate(
        quiz_questions
    ):

        user_answer = user_answers[
            index
        ]

        if user_answer == "":

            unattempted += 1

        elif user_answer == question[
            "answer"
        ]:

            correct += 1

        else:

            wrong += 1

    total = len(
        quiz_questions
    )

    percentage = (
        (correct / total) * 100
        if total > 0
        else 0
    )

    minutes, seconds = divmod(
        elapsed,
        60
    )

    time_taken = (
        f"{minutes:02d}:"
        f"{seconds:02d}"
    )

    # Save score
    save_score(
        total,
        correct,
        wrong,
        unattempted,
        percentage,
        time_taken
    )

    if percentage >= 70:

        ring_color = GREEN
        message = "Excellent work!"

    elif percentage >= 40:

        ring_color = AMBER
        message = (
            "Good effort, "
            "keep practising!"
        )

    else:

        ring_color = RED
        message = (
            "Keep practising, "
            "you will improve!"
        )

    make_header(
        "Quiz Completed",
        f"{current_quiz_title}  |  "
        f"User: {current_user}"
    )

    ring = tk.Canvas(
        root,
        width=200,
        height=200,
        bg=BG,
        highlightthickness=0
    )

    ring.pack(
        pady=(20, 4)
    )

    ring.create_oval(
        20,
        20,
        180,
        180,
        outline=GREY,
        width=16
    )

    if percentage > 0:

        ring.create_arc(
            20,
            20,
            180,
            180,
            start=90,
            extent=-min(
                359.9,
                3.6 * percentage
            ),
            style="arc",
            outline=ring_color,
            width=16
        )

    ring.create_text(
        100,
        92,
        text=f"{percentage:.1f}%",
        font=(
            FONT,
            26,
            "bold"
        ),
        fill=TEXT
    )

    ring.create_text(
        100,
        126,
        text=f"{correct} / {total}",
        font=(
            FONT,
            12
        ),
        fill=MUTED
    )

    tk.Label(
        root,
        text=message,
        font=(
            FONT,
            15,
            "bold"
        ),
        bg=BG,
        fg=ring_color
    ).pack(
        pady=(0, 14)
    )

    stats = tk.Frame(
        root,
        bg=BG
    )

    stats.pack(
        pady=6
    )

    stat_items = [
        (
            str(total),
            "Total",
            PRIMARY
        ),
        (
            str(correct),
            "Correct",
            GREEN
        ),
        (
            str(wrong),
            "Wrong",
            RED
        ),
        (
            str(unattempted),
            "Not attempted",
            AMBER
        ),
        (
            time_taken,
            "Time taken",
            MUTED
        )
    ]

    for value, label, color in stat_items:

        make_stat_card(
            stats,
            value,
            label,
            color
        ).pack(
            side="left",
            padx=8
        )

    buttons = tk.Frame(
        root,
        bg=BG
    )

    buttons.pack(
        pady=(26, 10)
    )

    mistakes = (
        wrong +
        unattempted
    )

    if mistakes > 0:

        make_button(
            buttons,
            f"Review Mistakes ({mistakes})",
            show_review,
            font_size=13,
            padx=24,
            pady=11
        ).pack(
            side="left",
            padx=8
        )

    else:

        tk.Label(
            buttons,
            text="Perfect score! Nothing to review.",
            font=(
                FONT,
                13,
                "bold"
            ),
            bg=BG,
            fg=GREEN
        ).pack(
            side="left",
            padx=12
        )

    make_button(
        buttons,
        "Retry Quiz",
        lambda: start_quiz(
            quiz_questions,
            current_quiz_title
        ),
        bg="#0284C7",
        hover=shade(
            "#0284C7",
            0.85
        ),
        font_size=13,
        padx=24,
        pady=11
    ).pack(
        side="left",
        padx=8
    )

    make_button(
        buttons,
        "Leaderboard",
        show_leaderboard,
        bg=PRIMARY,
        hover=PRIMARY_DARK,
        font_size=13,
        padx=24,
        pady=11
    ).pack(
        side="left",
        padx=8
    )

    make_button(
        buttons,
        "Back to Topics",
        show_topics,
        bg=HOVER_BG,
        fg=PRIMARY,
        hover="#E0E7FF",
        font_size=13,
        padx=24,
        pady=11
    ).pack(
        side="left",
        padx=8
    )


# ============================================================
# REVIEW SCREEN
# ============================================================

def show_review():

    clear_window()

    mistakes = [
        (
            index,
            question
        )
        for index, question in enumerate(
            quiz_questions
        )
        if user_answers[index]
        != question["answer"]
    ]

    header = make_header(
        "Review Mistakes",
        f"{len(mistakes)} question(s) "
        f"to revisit - "
        f"{current_quiz_title}"
    )

    header_button(
        header,
        "Back to Topics",
        show_topics
    )

    header_button(
        header,
        "Back to Result",
        show_result
    )

    container, canvas, inner = make_scrollable(
        root
    )

    container.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=15
    )

    wrap_labels = []

    def add_line(
        parent,
        text,
        bg,
        fg,
        top=3
    ):

        line = tk.Label(
            parent,
            text=text,
            font=(
                FONT,
                12
            ),
            bg=bg,
            fg=fg,
            anchor="w",
            justify="left",
            wraplength=800,
            padx=12,
            pady=6
        )

        line.pack(
            fill="x",
            pady=(top, 0)
        )

        wrap_labels.append(
            line
        )

    for index, question in mistakes:

        chosen = user_answers[
            index
        ]

        card = tk.Frame(
            inner,
            bg=CARD,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        card.pack(
            fill="x",
            padx=4,
            pady=8
        )

        tk.Frame(
            card,
            bg=(
                RED
                if chosen
                else AMBER
            ),
            width=6
        ).pack(
            side="left",
            fill="y"
        )

        content = tk.Frame(
            card,
            bg=CARD
        )

        content.pack(
            side="left",
            fill="both",
            expand=True,
            padx=18,
            pady=14
        )

        tk.Label(
            content,
            text=f"Question {index + 1}",
            font=(
                FONT,
                10,
                "bold"
            ),
            bg=CARD,
            fg=PRIMARY,
            anchor="w"
        ).pack(
            fill="x"
        )

        question_label = tk.Label(
            content,
            text=question["question"],
            font=(
                FONT,
                14,
                "bold"
            ),
            bg=CARD,
            fg=TEXT,
            anchor="w",
            justify="left",
            wraplength=800
        )

        question_label.pack(
            fill="x",
            pady=(2, 8)
        )

        wrap_labels.append(
            question_label
        )

        if chosen:

            add_line(
                content,
                f"Your answer:  {chosen}",
                RED_BG,
                RED_TEXT
            )

        else:

            add_line(
                content,
                "Not attempted",
                AMBER_BG,
                AMBER
            )

        add_line(
            content,
            f"Correct answer:  "
            f"{question['answer']}",
            GREEN_BG,
            GREEN_TEXT
        )

    def on_resize(event):

        for label in wrap_labels:

            label.config(
                wraplength=max(
                    event.width - 140,
                    300
                )
            )

    canvas.bind(
        "<Configure>",
        on_resize,
        add="+"
    )


# ============================================================
# LEADERBOARD
# ============================================================

def show_leaderboard():

    clear_window()

    header = make_header(
        "Leaderboard",
        "Quiz performance of all users"
    )

    header_button(
        header,
        "Back",
        show_home
    )

    container, canvas, inner = make_scrollable(
        root
    )

    container.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=20
    )

    if not leaderboard:

        tk.Label(
            inner,
            text="No quiz attempts yet.",
            font=(
                FONT,
                18,
                "bold"
            ),
            bg=BG,
            fg=MUTED
        ).pack(
            pady=80
        )

        return

    # Sort by percentage first
    # and score second.

    sorted_scores = sorted(
        leaderboard,
        key=lambda item: (
            item.get(
                "percentage",
                0
            ),
            item.get(
                "score",
                0
            )
        ),
        reverse=True
    )

    title_frame = tk.Frame(
        inner,
        bg=PRIMARY
    )

    title_frame.pack(
        fill="x",
        pady=(0, 5)
    )

    headings = [
        ("Rank", 8),
        ("User", 22),
        ("Topic", 35),
        ("Score", 12),
        ("Percentage", 15),
        ("Time", 12)
    ]

    for heading, width in headings:

        tk.Label(
            title_frame,
            text=heading,
            width=width,
            font=(
                FONT,
                11,
                "bold"
            ),
            bg=PRIMARY,
            fg="white",
            pady=10
        ).pack(
            side="left"
        )

    for rank, item in enumerate(
        sorted_scores,
        start=1
    ):

        row_bg = (
            CARD
            if rank % 2
            else HOVER_BG
        )

        row = tk.Frame(
            inner,
            bg=row_bg,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        row.pack(
            fill="x"
        )

        values = [
            str(rank),
            item.get(
                "name",
                "-"
            ),
            item.get(
                "topic",
                "-"
            ),
            (
                f"{item.get('score', 0)} / "
                f"{item.get('total', 0)}"
            ),
            (
                f"{item.get('percentage', 0)}%"
            ),
            item.get(
                "time",
                "-"
            )
        ]

        for index, (
            value,
            heading
        ) in enumerate(
            zip(
                values,
                headings
            )
        ):

            width = heading[1]

            fg = TEXT

            if index == 0:

                if rank == 1:

                    fg = GREEN

                elif rank == 2:

                    fg = AMBER

                elif rank == 3:

                    fg = PRIMARY

            tk.Label(
                row,
                text=value,
                width=width,
                font=(
                    FONT,
                    10,
                    "bold"
                    if index == 0
                    else "normal"
                ),
                bg=row_bg,
                fg=fg,
                anchor="center",
                pady=9
            ).pack(
                side="left"
            )


# ============================================================
# START APPLICATION
# ============================================================

if load_problems:

    shown = load_problems[:8]

    if len(load_problems) > 8:

        shown.append(
            f"... and "
            f"{len(load_problems) - 8} more"
        )

    messagebox.showwarning(
        "Problems in question files",
        "\n".join(shown)
    )


# ------------------------------------------------------------
# Decide Registration or Login
# ------------------------------------------------------------

if users:

    show_login()

else:

    show_registration()


root.mainloop()