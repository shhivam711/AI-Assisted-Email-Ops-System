from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from normalizers import normalize_email
from rules import apply_rules
from sheets import get_sheets_service, append_row, SPREADSHEET_ID
from datetime import datetime
from slack import send_slack_alert
from ai_explainer import explain_email
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/spreadsheets"
        ]

# Starting gmail service
def get_gmail_service():
    logging.info("Starting OAuth...")

    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json",
        SCOPES
    )

    creds = flow.run_local_server(
        port=8080,
        open_browser=True
    )

    logging.info("OAuth successful")
    service = build("gmail", "v1", credentials=creds)
    return service

# Fetching last 5 mails
def fetch_last_emails(service, max_results=5):
    result = service.users().messages().list(
        userId="me",
        maxResults=max_results
    ).execute()

    return result.get("messages", [])

# Message details are fetched here
def get_message_details(service, msg_id):
    message = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="metadata",
        metadataHeaders=["From", "Subject", "Date"]
    ).execute()

    headers = message.get("payload", {}).get("headers", [])
    header_dict = {h["name"]: h["value"] for h in headers}

    return {
    "id": msg_id,
    "from": header_dict.get("From", ""),
    "subject": header_dict.get("Subject", ""),
    "snippet": message.get("snippet", ""),
    "timestamp": message.get("internalDate", "")
    }

# Checking for duplicate mails
def is_message_id_in_sheet(service,message_id: str) -> bool:
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!G:G"   # G column me message_id hai
    ).execute()

    rows = result.get("values", [])

    for row in rows:
        if row and row[0] == message_id:
            return True

    return False


def main():
    logging.info("=== Email Ops System (No venv) ===")

    service = get_gmail_service()
    messages = fetch_last_emails(service)
    sheets_service = get_sheets_service(service._http.credentials)
    logging.info(f"Fetched {len(messages)} emails\n")

    for msg in messages:
        raw = get_message_details(service, msg["id"])
        email = normalize_email(raw)

        # If duplicate email found , skip it
        if is_message_id_in_sheet(sheets_service , email.message_id):
            logging.info(
                f"Duplicate email skipped | message_id={email.message_id}"
            )
            continue   # yahin STOP, next email pe jao

        category, rule_id = apply_rules(email)

        # Adding try except so code dont crash in case of api failure
        try:
            explanation = explain_email(email, category, rule_id)
        except Exception as e:
            logging.error(f"AI explanation failed for email : {email.message_id} and the reason is {e}")
            explanation = ""

        row = [
            email.received_at.strftime("%Y-%m-%d %H:%M:%S") if email.received_at else "",
            email.sender,
            email.subject,
            category,
            rule_id,
            explanation,
            email.message_id
        ]

        try:
            append_row(sheets_service, row)
            logging.info(f"Logged: {email.subject}")
        except Exception as e:
            logging.error(f"Google sheet logging failed. Reason:{e}")
        
        try:
            if category == "ACTION_REQUIRED":
                message = (
                    "*🚨 Action Required Email*\n"
                    f"*From:* {email.sender}\n"
                    f"*Subject:* {email.subject}\n"
                    f"*Rule:* {rule_id}")

                send_slack_alert(message)

        except Exception as e:
            logging.error(f"Slack logging failed for the process {email.subject} and reason is {e}")

        logging.info(f"Processed: {email.subject}")

    logging.info("Email Ops run completed successfully")


# Making the system not to crash at unavoidable errors.
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("System stopped manually by user (Ctrl+C)")
    except Exception as e:
        logging.critical(
            f"System crashed due to unexpected error | error={e}",
            exc_info=True # gives complete explanation and details of error
        )
