# gui_email_sender.py
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import time
import re
import csv
import json
from datetime import datetime

import email_utils
from email_utils import load_template, read_csv_file, send_message

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

APP_NAME = "Automated Email Sender"
CONFIG_FILE = "config.json"


class EmailSenderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1020x720")

        # ✅ FIX: enable minimize & fullscreen
        self.root.resizable(True, True)
        self.root.minsize(1020, 720)

        # ---------- App Icon ----------
        if os.path.exists("app_icon.ico"):
            self.root.iconbitmap("app_icon.ico")

        # ---------- Theme ----------
        self.is_dark_mode = False
        self.default_bg = "#f4f6f8"
        self.root.configure(bg=self.default_bg)

        # ---------- Load Config ----------
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.load_config()

        # ---------- Style ----------
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabelFrame", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        # ---------- Header ----------
        header = tk.Label(
            root,
            text=f"{APP_NAME}\nEnterprise Email Automation Tool",
            font=("Segoe UI", 14, "bold"),
            bg=self.default_bg
        )
        header.pack(pady=8)

        # ================= CSV =================
        csv_frame = ttk.LabelFrame(root, text="📄 CSV Upload & Preview")
        csv_frame.pack(fill="x", padx=12, pady=6)

        top = ttk.Frame(csv_frame)
        top.pack(fill="x", padx=6, pady=4)

        self.csv_path_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.csv_path_var, width=78).pack(side="left", padx=5)
        ttk.Button(top, text="Browse CSV", command=self.browse_csv).pack(side="left", padx=5)
        ttk.Button(top, text="Clear", command=self.clear_csv).pack(side="left", padx=5)

        self.csv_status = ttk.Label(csv_frame, text="No CSV loaded", foreground="gray")
        self.csv_status.pack(anchor="w", padx=10)

        self.tree = ttk.Treeview(csv_frame, columns=("name", "email", "subject"), show="headings", height=6)
        for col in ("name", "email", "subject"):
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=320)
        self.tree.pack(fill="x", padx=8, pady=6)

        # ================= SMTP =================
        smtp_frame = ttk.LabelFrame(root, text="📡 SMTP Configuration")
        smtp_frame.pack(fill="x", padx=12, pady=6)

        ttk.Label(smtp_frame, text="Server").grid(row=0, column=0, padx=6, pady=4)
        self.smtp_server_var = tk.StringVar(value=self.smtp_server)
        ttk.Entry(smtp_frame, textvariable=self.smtp_server_var, width=30).grid(row=0, column=1)

        ttk.Label(smtp_frame, text="Port").grid(row=0, column=2, padx=6)
        self.smtp_port_var = tk.IntVar(value=self.smtp_port)
        ttk.Entry(smtp_frame, textvariable=self.smtp_port_var, width=8).grid(row=0, column=3)

        # ================= CONTROLS =================
        ctl = ttk.LabelFrame(root, text="⚙ Controls")
        ctl.pack(fill="x", padx=12, pady=6)

        ttk.Label(ctl, text="Template File").grid(row=0, column=0, padx=6, pady=4)
        self.template_path_var = tk.StringVar(value="email_template.txt")
        ttk.Entry(ctl, textvariable=self.template_path_var, width=62).grid(row=0, column=1)
        ttk.Button(ctl, text="Browse", command=self.browse_template).grid(row=0, column=2)

        ttk.Label(ctl, text="Attachment").grid(row=1, column=0, padx=6, pady=4)
        self.attachment_var = tk.StringVar()
        ttk.Entry(ctl, textvariable=self.attachment_var, width=62).grid(row=1, column=1)
        ttk.Button(ctl, text="Browse", command=self.browse_attachment).grid(row=1, column=2)

        btns = ttk.Frame(ctl)
        btns.grid(row=2, column=0, columnspan=3, pady=10)

        # ✅ COLORED BUTTONS (UI ONLY)
        self.start_btn = tk.Button(btns, text="Start Sending", bg="#22c55e", fg="white",
                                   width=16, command=self.confirm_and_start, state="disabled")
        self.preview_btn = tk.Button(btns, text="Preview Email", bg="#3b82f6", fg="white",
                                     width=16, command=self.preview_email, state="disabled")
        self.stop_btn = tk.Button(btns, text="Stop", bg="#ef4444", fg="white",
                                  width=12, command=self.stop_sending, state="disabled")
        logs_btn = tk.Button(btns, text="Open Logs", bg="#111827", fg="white",
                             width=12, command=self.open_logs)

        self.start_btn.pack(side="left", padx=6)
        self.preview_btn.pack(side="left", padx=6)
        self.stop_btn.pack(side="left", padx=6)
        logs_btn.pack(side="left", padx=6)

        # ================= PROGRESS =================
        prog = ttk.LabelFrame(root, text="📊 Progress")
        prog.pack(fill="x", padx=12, pady=6)

        self.progress = ttk.Progressbar(prog, length=760)
        self.progress.pack(padx=6, pady=4)
        self.progress_label = ttk.Label(prog, text="Idle")
        self.progress_label.pack(anchor="w", padx=10)

        # ================= LOGS =================
        logs = ttk.LabelFrame(root, text="📝 Live Logs")
        logs.pack(fill="both", expand=True, padx=12, pady=6)

        log_frame = ttk.Frame(logs)
        log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(
            log_frame,
            bg="#0f172a",
            fg="#e5e7eb",
            font=("Consolas", 10),
            insertbackground="white"
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ================= STATE =================
        self.recipients = []
        self.valid_recipients = []
        self._stop_event = threading.Event()

        self.append_log("Application started successfully.")

    # ================= CONFIG =================
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.smtp_server = data.get("smtp_server", self.smtp_server)
                self.smtp_port = data.get("smtp_port", self.smtp_port)

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(
                {
                    "smtp_server": self.smtp_server_var.get(),
                    "smtp_port": self.smtp_port_var.get(),
                },
                f,
                indent=4,
            )

    # ================= CSV =================
    def browse_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        self.csv_path_var.set(path)
        self.recipients = read_csv_file(path)
        self.validate_csv()

    def validate_csv(self):
        self.valid_recipients.clear()
        self.tree.delete(*self.tree.get_children())

        for r in self.recipients:
            email = r.get("email", "")
            if EMAIL_REGEX.match(email):
                self.valid_recipients.append(r)
                self.tree.insert("", "end", values=(r.get("name"), email, r.get("subject")))

        if self.valid_recipients:
            self.csv_status.config(
                text=f"Valid rows: {len(self.valid_recipients)} / {len(self.recipients)}",
                foreground="green",
            )
            self.start_btn.config(state="normal")
            self.preview_btn.config(state="normal")

    def clear_csv(self):
        self.csv_path_var.set("")
        self.valid_recipients.clear()
        self.tree.delete(*self.tree.get_children())
        self.start_btn.config(state="disabled")
        self.preview_btn.config(state="disabled")
        self.csv_status.config(text="No CSV loaded", foreground="gray")

    # ================= PREVIEW =================
    def preview_email(self):
        r = self.valid_recipients[0]
        template = load_template(self.template_path_var.get())
        body = template.format(name=r["name"], subject=r["subject"])
        messagebox.showinfo("Email Preview", f"Subject: {r['subject']}\n\n{body}")

    # ================= SEND =================
    def confirm_and_start(self):
        if messagebox.askyesno("Confirm", f"Send {len(self.valid_recipients)} emails?"):
            self.start_sending()

    def start_sending(self):
        template = load_template(self.template_path_var.get())
        self._stop_event.clear()
        self.progress["maximum"] = len(self.valid_recipients)
        self.progress["value"] = 0
        self.progress_label.config(text="Sending...")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        threading.Thread(target=self._send_worker, args=(template,), daemon=True).start()

    def stop_sending(self):
        self._stop_event.set()

    def _send_worker(self, template):
        email_utils.SMTP_SERVER = self.smtp_server_var.get()
        email_utils.SMTP_PORT = self.smtp_port_var.get()
        self.save_config()

        for idx, r in enumerate(self.valid_recipients, start=1):
            if self._stop_event.is_set():
                break
            body = template.format(name=r["name"], subject=r["subject"])
            success, logline = send_message(
                r["email"], r["subject"], body,
                attachment_path=self.attachment_var.get() or None
            )
            self.append_log(logline)
            self.progress["value"] = idx
            self.progress_label.config(text=f"{idx} / {len(self.valid_recipients)}")
            time.sleep(2)

        self.progress_label.config(text="Completed")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        messagebox.showinfo("Done", "Email sending completed.")

    # ================= UTILS =================
    def append_log(self, text):
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")

    def browse_template(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.template_path_var.set(path)

    def browse_attachment(self):
        path = filedialog.askopenfilename()
        if path:
            self.attachment_var.set(path)

    def open_logs(self):
        if os.path.exists("logs/activity_log.txt"):
            os.startfile("logs/activity_log.txt")


if __name__ == "__main__":
    root = tk.Tk()
    EmailSenderGUI(root)
    root.mainloop()
