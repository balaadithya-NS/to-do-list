import tkinter as tk
from tkinter import messagebox
from sqlite3 import connect
from datetime import date

# Colors and fonts
bg = "#242424"
fg = "#333333"
text = "#FFFFFF"
accent = "#5B8DEF"
green = "#4CAF50"
red = "#E05252"
font = ("Arial", 16)
title_font = ("Arial", 30, "bold")

# Database
con = connect("data.db")
cur = con.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS data (
        task TEXT,
        task_done TEXT,
        date TEXT
    )
""")
con.commit()


def read():
    cur.execute("SELECT rowid, * FROM data ORDER BY rowid DESC")
    return cur.fetchall()


def write(task):
    cur.execute(
        "INSERT INTO data VALUES (?, ?, ?)",
        (task, "No", date.today().isoformat())
    )
    con.commit()


def refresh_tasks():
    for widget in task_frame.winfo_children():
        widget.destroy()

    tasks = read()

    if not tasks:
        tk.Label(
            task_frame,
            text="No tasks yet. Add your first task!",
            bg=bg, fg="#AAAAAA", font=font
        ).pack(pady=30)
        return

    for task_id, task, done, task_date in tasks:
        row = tk.Frame(task_frame, bg=fg)
        row.pack(fill="x", padx=10, pady=5)

        completed = tk.BooleanVar(value=(done == "Yes"))

        check = tk.Checkbutton(
            row,
            text=task,
            variable=completed,
            bg=fg,
            fg=text,
            selectcolor=bg,
            activebackground=fg,
            activeforeground=text,
            font=font,
            anchor="w",
            command=lambda i=task_id, v=completed:
                toggle_task(i, v)
        )
        check.pack(side="left", fill="x", expand=True, padx=10, pady=8)

        tk.Label(
            row,
            text=task_date,
            bg=fg, fg="#BBBBBB",
            font=("Arial", 11)
        ).pack(side="left", padx=10)

        tk.Button(
            row,
            text="Delete",
            bg=red, fg=text,
            font=("Arial", 11),
            relief="flat",
            command=lambda i=task_id: delete_task(i)
        ).pack(side="right", padx=10, pady=8)


def add_task():
    task = add_data_box.get().strip()

    if not task:
        messagebox.showwarning("Empty task", "Please enter a task.")
        return

    write(task)
    add_data_box.delete(0, tk.END)
    refresh_tasks()


def toggle_task(task_id, completed):
    cur.execute(
        "UPDATE data SET task_done = ? WHERE rowid = ?",
        ("Yes" if completed.get() else "No", task_id)
    )
    con.commit()


def delete_task(task_id):
    cur.execute("DELETE FROM data WHERE rowid = ?", (task_id,))
    con.commit()
    refresh_tasks()


def main():
    global task_frame, add_data_box

    wn = tk.Tk()
    wn.title("Daily Tasks")
    wn.geometry("1100x750")
    wn.resizable(False, False)
    wn.config(bg=bg)

    # Header
    tk.Label(
        wn,
        text="DAILY TASKS",
        bg=bg, fg=text,
        font=title_font
    ).place(relx=0.5, rely=0.07, anchor="center")

    tk.Label(
        wn,
        text=date.today().strftime("%A, %d %B %Y"),
        bg=bg, fg="#BBBBBB",
        font=("Arial", 13)
    ).place(relx=0.5, rely=0.13, anchor="center")

    # Task input
    add_data_box = tk.Entry(
        wn,
        font=font,
        bg=fg,
        fg=text,
        insertbackground=text,
        relief="flat"
    )
    add_data_box.place(
        relx=0.43, rely=0.23,
        anchor="center", width=600, height=45
    )

    add_data_box.bind("<Return>", lambda event: add_task())

    tk.Button(
        wn,
        text="+ Add Task",
        font=("Arial", 14, "bold"),
        bg=accent,
        fg=text,
        activebackground=accent,
        relief="flat",
        command=add_task
    ).place(
        relx=0.82, rely=0.23,
        anchor="center", width=150, height=45
    )

    # Task list container
    tk.Label(
        wn,
        text="YOUR TASKS",
        bg=bg, fg=text,
        font=("Arial", 18, "bold")
    ).place(relx=0.08, rely=0.33, anchor="w")

    container = tk.Frame(wn, bg=bg)
    container.place(
        relx=0.5, rely=0.66,
        anchor="center", width=950, height=430
    )

    canvas = tk.Canvas(
        container, bg=bg,
        highlightthickness=0
    )
    scrollbar = tk.Scrollbar(
        container, orient="vertical",
        command=canvas.yview
    )

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    task_frame = tk.Frame(canvas, bg=bg)
    window_id = canvas.create_window(
        (0, 0), window=task_frame, anchor="nw"
    )

    task_frame.bind(
        "<Configure>",
        lambda event: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.bind(
        "<Configure>",
        lambda event: canvas.itemconfigure(
            window_id, width=event.width
        )
    )

    refresh_tasks()
    wn.mainloop()


if __name__ == "__main__":
    main()
