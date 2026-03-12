# MailPulse — AI Email-to-WhatsApp Agent

MailPulse is a personal automation agent that monitors your Gmail inbox, uses Google Gemini AI to intelligently summarize each incoming email, and delivers the summary directly to a WhatsApp contact — all without you lifting a finger.

It classifies every email as **spam/phishing** or **legitimate**, and for legitimate emails it extracts the subject, key points, relevant links, and any action items. Summaries are formatted with WhatsApp bold markdown so they're easy to read on your phone.

---

## How It Works

```
Gmail Inbox  →  IMAP Fetch  →  Gemini AI Summary  →  WhatsApp Web (Selenium)  →  Your Phone
```

1. The agent polls your Gmail inbox every 30 minutes via IMAP.
2. New emails (arrived since the last run) are fetched one by one.
3. Each email body is sent to Google Gemini with a detailed triage prompt.
4. Gemini returns a structured JSON response classifying the email and extracting key information.
5. The agent formats the result into a WhatsApp-friendly message and sends it via WhatsApp Web using Selenium.
6. The last processed email UID is saved to `state.json` so emails are never processed twice.

**First run:** The browser opens visibly so you can scan the WhatsApp Web QR code. After that, the Chrome session is saved locally and all subsequent runs are fully headless (no visible browser window).

---

## What a Summary Looks Like

**For a normal email:**
```
*Subject:* Your invoice #1042 is ready
*Importance:* HIGH

*Summary*
- Invoice #1042 for $320 has been generated
- Payment due by March 20, 2026

*Links Worth Opening*
- View your invoice
  https://billing.example.com/invoice/1042

*Actions*
- Review and pay invoice before March 20
```

**For a spam/phishing email:**
```
*Potential Spam Email*

*Subject:* You've won a $1,000 gift card!

*Reason*
- Unsolicited prize claim with urgency language
- Requests personal information

*Keywords detected*
- "you've won"
- "claim now"
- "limited time"
```

---

## Requirements

- Python 3.10+
- Google Chrome installed
- A Gmail account
- A Google Gemini API key
- WhatsApp account linked to WhatsApp Web

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd email

python -m venv env_email
source env_email/bin/activate   # On Windows: env_email\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and fill in each value (see details below):

```env
EMAIL_ADDRESS=you@gmail.com
EMAIL_APP_PASSWORD=abcdefghijklmnop (12 letters code)
GEMINI_API_KEY=AIza...
WHATSAPP_CONTACT_NAME=Self (You)
MODEL=gemini-2.5-flash
```

---

## Environment Variables Explained

### `EMAIL_ADDRESS`
Your full Gmail address, e.g. `you@gmail.com`.

---

### `EMAIL_APP_PASSWORD`
This is **not** your regular Gmail password. Google requires a dedicated **App Password** for third-party apps accessing Gmail via IMAP.

**Steps to generate one:**
1. Go to your Google Account → [Security](https://myaccount.google.com/security)
2. Make sure **2-Step Verification** is enabled (required for App Passwords)
3. Search for **"App Passwords"** in the search bar or go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Under "App name", type something like `MailPulse` and click **Create**
5. Google will display a 16-character password (e.g. `abcd efgh ijkl mnop`) — copy this into your `.env` file

> The spaces in the password are fine to include or remove — both work.

---

### `GEMINI_API_KEY`
Your Google Gemini API key.

**Steps to get one:**
1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click **Create API Key**
3. Copy the key into your `.env` file

---

### `WHATSAPP_CONTACT_NAME`
The **exact name** of the WhatsApp contact or group you want to send summaries to. This is used to search for the chat in WhatsApp Web.

- To send messages **to yourself**, open WhatsApp and find your own contact — it's usually called **"You"**, **"Self"**, or your own name. On WhatsApp Web, you can message yourself by searching your own name or number.
- To send to someone else, use the exact name as it appears in your WhatsApp contact list, e.g. `John Doe`.
- To send to a group, use the exact group name, e.g. `Family`.

> Tip: The easiest setup is to message yourself. On WhatsApp, go to **New Chat → Your own number** to start a "Saved Messages"-style chat with yourself.

---

### `MODEL`
The Gemini model to use. Defaults to `gemini-2.5-flash`, which is fast and cost-effective.
Other options: `gemini-2.0-flash`, `gemini-1.5-pro`.

---

## First Run — QR Code Scan

On the very first run, WhatsApp Web requires you to link your device by scanning a QR code.

The agent handles this automatically:
- It detects that no saved session exists
- It opens a **visible Chrome window** and loads WhatsApp Web
- Scan the QR code with your phone (WhatsApp → Linked Devices → Link a Device)
- Once scanned, the agent continues automatically
- The session is saved in `./chrome_session/` — all future runs will be **headless** (no window)

> If WhatsApp logs you out (after ~14 days of inactivity or if you manually unlink the device), the QR flow will trigger again automatically.

---

## Running the Agent

```bash
source env_email/bin/activate
python main.py
```

The agent will:
1. Mark all existing emails as already seen (so you only get summaries for new ones going forward)
2. Begin polling every 30 minutes
3. Print status updates to the terminal

To keep it running in the background, you can use `nohup` or a process manager like `screen` or `pm2`:

```bash
nohup python main.py > mailpulse.log 2>&1 &
```

---

## Project Structure

```
email/
├── main.py              # Entry point — polling loop and orchestration
├── gmail_reader.py      # IMAP connection, email fetching, UID state management
├── summarizer.py        # Gemini AI prompt, JSON parsing, WhatsApp message formatting
├── whatsapp_sender.py   # Selenium browser automation for WhatsApp Web
├── config.py            # Loads environment variables from .env
├── requirements.txt     # Python dependencies
├── .env                 # Your secrets (never commit this)
├── .env.example         # Template for .env
├── state.json           # Tracks the last processed email UID (auto-generated)
└── chrome_session/      # Saved Chrome/WhatsApp Web session (auto-generated)
```

---

## Notes & Limitations

- **Gmail only:** The IMAP server is hardcoded to `imap.gmail.com`. Other providers would need a config change.
- **Plain text emails only:** HTML-only emails will be sent as empty bodies to Gemini. Most emails include a plain text part.
- **WhatsApp Web session timeout:** WhatsApp Web sessions expire after approximately 14 days of inactivity. The QR scan will be triggered again automatically.
- **Rate limits:** If you receive many emails in a short time, Gemini API rate limits may cause summarization failures. The agent will retry these on the next poll.
