from __future__ import annotations

import os
import json
import base64
from email import message_from_string
from email.utils import parsedate_to_datetime
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from phrases import REJECTION_PHRASES

SCOPES: list[str] = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service() -> Any:
    creds = None
    # the cached credentials which are auto created when you have credentials.json. see below.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # credentials.json is from OAuth client ID/secret (from Google Cloud Console)
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    service = build("gmail", "v1", credentials=creds)
    return service


def get_message_ids_and_times(
    service: Any,
    query: str,
    cache_file: str = "rejection_messages_full.json",
) -> list[dict]:
    """Get all message data (date, from, subject, body) for a query with caching"""

    if os.path.exists(cache_file):
        print(f"Found cached messages in '{cache_file}'")
        response = input("Use cached data? (y/n): ").strip().lower()
        if response == "y":
            with open(cache_file, "r") as f:
                cached_data = json.load(f)
            print(f"✅ Loaded {len(cached_data)} messages from cache! 🦘\n")
            return cached_data

    print("Fetching fresh message data from Gmail... ")
    messages_data: list[dict] = []
    next_page_token: str | None = None
    total_fetched = 0

    while True:
        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, pageToken=next_page_token, maxResults=500)
            .execute()
        )

        messages = results.get("messages", [])

        for msg in messages:
            # First call: get headers
            meta_msg = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=msg["id"],
                    format="metadata",
                    metadataHeaders=["Date", "From", "Subject"],
                )
                .execute()
            )

            headers = meta_msg["payload"]["headers"]
            date_value: str | None = None
            from_email = ""
            subject = ""

            for header in headers:
                name_lower = header["name"].lower()
                if name_lower == "date":
                    try:
                        date_value = parsedate_to_datetime(header["value"]).isoformat()
                    except Exception:
                        pass
                elif name_lower == "from":
                    from_email = header["value"]
                elif name_lower == "subject":
                    subject = header["value"]

            # Second call: get body separately
            raw_msg = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="raw")
                .execute()
            )

            body_text = ""
            try:
                raw_bytes = base64.urlsafe_b64decode(raw_msg["raw"])
                email_msg = message_from_string(raw_bytes.decode("UTF-8"))

                if email_msg.is_multipart():
                    for part in email_msg.walk():
                        if part.get_content_type() == "text/plain":
                            body_text = part.get_payload(decode=True).decode(
                                "utf-8", errors="ignore"
                            )
                            break
                else:
                    body_text = email_msg.get_payload(decode=True).decode(
                        "utf-8", errors="ignore"
                    )
            except Exception:
                body_text = ""

            messages_data.append(
                {
                    "id": msg["id"],
                    "date": date_value,
                    "from": from_email,
                    "subject": subject,
                    "body": body_text,
                }
            )

            total_fetched += 1
            if total_fetched % 50 == 0:
                print(f"    Fetched {total_fetched} messages...")

        next_page_token = results.get("nextPageToken")
        if not next_page_token:
            break

    print(f"\n💾 Saving messages to '{cache_file}'...")
    with open(cache_file, "w") as f:
        json.dump(messages_data, f, indent=2)
    print("✅ Cache saved!")

    return messages_data


def main() -> None:
    print("Connecting to Gmail... ")
    service = get_gmail_service()

    query_parts = [f'"{phrase}"' for phrase in REJECTION_PHRASES]
    combo_reject_query = f"({' OR '.join(query_parts)}) -in:chats -in:trash -in:spam -from:me"

    print("\nFetching rejection emails... ☠️")
    rejection_times = get_message_ids_and_times(service, combo_reject_query)
    print(f"✅ Fetched {len(rejection_times)} emails!\n")

    print("Run 'python analysis.py' to generate charts 📊")


if __name__ == "__main__":
    main()
