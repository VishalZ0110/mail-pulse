import time
import os

from gmail_reader import initialize_last_uid, fetch_new_emails, save_last_uid
from summarizer import summarize_email
from whatsapp_sender import start_browser, send_message


def is_first_run():
    """Check if this is the first run by looking for existing session data."""
    session_dir = "./chrome_session/Default"
    if not os.path.exists(session_dir):
        return True
    # If the directory exists but has very few files, likely no session yet
    return len(os.listdir(session_dir)) < 5


def main():

    print("Starting Email → WhatsApp agent")
    print("Will poll every 30 minutes")
    # ignore old emails
    initialize_last_uid(hard_code_last_uid=0)

    while True:

        try:
            first_run = is_first_run()
            if first_run:
                print("First run detected — opening browser window for QR code scan...")
            else:
                print("Session found — running in headless mode.")

            emails = fetch_new_emails()
            for email in emails:
                print(f"Processing email UID {email['uid']} ({email['subject']})")
                driver = start_browser(headless=not first_run)
                try:
                    message = summarize_email(email["body"])
                    send_message(driver, message)
                    save_last_uid(email["uid"])
                except Exception as e:
                    print(f"Error processing email UID {email['uid']} ({email['subject']}): {e}")
                    driver.quit()
                    break
                driver.quit()

        except Exception as e:
            print("Error:", e)

        print("Will poll after 30 minutes")
        time.sleep(1800)


if __name__ == "__main__":
    main()
