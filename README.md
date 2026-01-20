# 📧 Automated Email Sender (GUI-Based)

An **industry-grade, GUI-based Automated Email Sender** built using **Python and Tkinter**.  
This application allows users to upload a CSV file containing recipient details and send personalized emails in bulk using SMTP (Gmail supported), with progress tracking, logging, and preview functionality.

---

## 🚀 Features

- 📄 **CSV Upload & Validation**
  - Upload recipient data using a CSV file
  - Validates email format automatically
  - Displays valid rows count before sending

- ✉️ **Personalized Email Sending**
  - Uses dynamic placeholders (`{name}`, `{subject}`)
  - Supports plain text email templates
  - Optional file attachment support

- 🖥️ **Graphical User Interface (GUI)**
  - Built using Tkinter
  - User-friendly and non-technical friendly
  - Supports minimize, maximize, and fullscreen

- 📊 **Progress Tracking**
  - Real-time progress bar
  - Live status updates during sending

- 📝 **Live Logs Panel**
  - Displays real-time email activity
  - Scrollable, high-contrast, readable logs
  - Persistent log file stored locally

- 🔍 **Email Preview**
  - Preview the first email before sending
  - Helps avoid mistakes in templates

- ⚙️ **SMTP Configuration Panel**
  - Configure SMTP server and port
  - Configuration saved using `config.json`

- 🎨 **Professional UI**
  - Color-coded action buttons:
    - 🟢 Start (Send)
    - 🔵 Preview
    - 🔴 Stop
    - ⚫ Open Logs

- 📦 **Executable Support**
  - Can be converted into a standalone `.exe` using PyInstaller

---

## 🛠️ Tech Stack

- **Language:** Python 3.x  
- **GUI:** Tkinter  
- **Email:** `smtplib`, `email.mime`  
- **File Handling:** CSV, JSON  
- **Threading:** Background email sending  
- **Packaging:** PyInstaller  

---

## 📂 Project Structure

Automated_Email_Sender/
│
├── gui_email_sender.py # Main GUI application
├── email_utils.py # Email sending and logging utilities
├── config.py # Email credentials (App Password)
├── config.json # Saved SMTP configuration
├── email_template.txt # Email body template
├── recipients.csv # Sample CSV file
├── logs/
│ └── activity_log.txt # Email activity logs
├── app_icon.ico # Application icon
├── README.md # Project documentation


📝 Email Template Format
Hello {name},

This is a reminder regarding: {subject}.

Regards,
Automation Team

Use Cases

Internship / Academic projects
Internal company notifications
HR bulk communication
Event reminders
Marketing & outreach automation (small scale)

📈 Industry Evaluation

✔ Clean architecture
✔ GUI-based automation
✔ Safe credential handling
✔ Threaded execution
✔ Logging & validation
✔ Production-ready design


👨‍💻 Author

Gowtham R
Front-End & Python Developer
Automated Email Systems | GUI Applications