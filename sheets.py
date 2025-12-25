from googleapiclient.discovery import build

SPREADSHEET_ID = "1w7ic9d7rpz2WGkbn8_sSQrlJtN8qUJk7k-G7Dxxe_NA"
RANGE_NAME = "Sheet1!A:G"


def get_sheets_service(creds):
    return build("sheets", "v4", credentials=creds)


def append_row(service, row):
    body = {
        "values": [row]
    }

    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        body=body
    ).execute()
