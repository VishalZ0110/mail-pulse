import json
import os
from imapclient import IMAPClient
import pyzmail
import config

STATE_FILE = "state.json"


def load_last_uid():
    if not os.path.exists(STATE_FILE):
        return None

    with open(STATE_FILE, "r") as f:
        data = json.load(f)
        return data.get("last_uid")


def save_last_uid(uid):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_uid": uid}, f)


def initialize_last_uid(hard_code_last_uid=None):
    """
    Called once when the bot starts.
    It stores the latest email UID so older emails are ignored.
    """
    if hard_code_last_uid is not None:
        save_last_uid(hard_code_last_uid)
        return

    with IMAPClient(config.IMAP_SERVER) as server:

        server.login(config.EMAIL_ADDRESS, config.EMAIL_APP_PASSWORD)
        server.select_folder("INBOX")

        uids = server.search(["ALL"])

        if not uids:
            save_last_uid(0)
            return

        latest_uid = max(uids)
        save_last_uid(latest_uid)


def fetch_new_emails():
    """
    Fetch only emails that arrived after last_uid
    """

    last_uid = load_last_uid()

    emails = []

    with IMAPClient(config.IMAP_SERVER) as server:

        server.login(config.EMAIL_ADDRESS, config.EMAIL_APP_PASSWORD)

        # readonly prevents marking messages as seen
        server.select_folder("INBOX", readonly=True)

        if last_uid is None:
            return []

        status = server.folder_status("INBOX", ["UIDNEXT"])
        uid_next = status[b'UIDNEXT']

        new_uids = server.search(f"UID {last_uid+1}:{uid_next}")

        if not new_uids:
            return []

        response = server.fetch(new_uids, ["BODY[]"])
        for uid, msg in response.items():

            email = pyzmail.PyzMessage.factory(msg[b"BODY[]"])

            subject = email.get_subject()

            if email.text_part:
                body = email.text_part.get_payload().decode(
                    email.text_part.charset or "utf-8"
                )
            else:
                body = ""

            emails.append(
                {
                    "uid": uid,
                    "subject": subject,
                    "body": body
                }
            )

    emails.sort(key=lambda e: e["uid"])
    return emails
