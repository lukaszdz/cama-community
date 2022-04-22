""" Google Sheets Interface """

import os
from math import floor
from string import ascii_uppercase
from typing import List, Tuple
import random

import pandas as pd  # type: ignore
from google.oauth2 import service_account  # type: ignore
from googleapiclient.discovery import build  # type: ignore

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

SHEET_NAME = "Cama BlockChain"
TAB_NAME = "THE MINT"


def build_creds_from_dict(config: dict) -> service_account.Credentials:
    env_credentials = {
        "type": config["TYPE"],
        "project_id": config["PROJECT_ID"],
        "private_key_id": config["PRIVATE_KEY_ID"],
        "private_key": config["PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": config["CLIENT_EMAIL"],
        "client_id": config["CLIENT_ID"],
        "auth_uri": config["AUTH_URI"],
        "token_uri": config["TOKEN_URI"],
        "auth_provider_x509_cert_url": config["AUTH_PROVIDER_X509_CERT_URL"],
        "client_x509_cert_url": config["CLIENT_X509_CERT_URL"],
    }
    service_account_credentials = service_account.Credentials.from_service_account_info(
        env_credentials, scopes=SCOPES
    )
    return service_account_credentials


def get_values_for_sheet_by_id_and_tab(
    config, spreadsheet_id, speadsheet_tab_name
) -> List:
    creds = build_creds_from_dict(config)
    sheets_service = build("sheets", "v4", credentials=creds).spreadsheets()
    result = (
        sheets_service.values()
        .get(spreadsheetId=spreadsheet_id, range=speadsheet_tab_name)
        .execute()
    )
    values = result.get("values", [])
    return values


def get_camas(config) -> pd.DataFrame:
    sheet_values = get_values_for_sheet_by_id_and_tab(
        config, config["SHEETS_DB_FILE_ID"], TAB_NAME
    )
    header_row_index = 0
    data_row_start_index = 1
    primary_key_col_index = 0
    num_cols = 4
    header = sheet_values[header_row_index][:num_cols]
    data = [
        row[:num_cols]
        for row in sheet_values[data_row_start_index:]
        if len(row) >= primary_key_col_index and row[primary_key_col_index] != ""
    ]
    camas_df = pd.DataFrame(data=data, columns=header)
    return camas_df


def get_camarrons(config: dict, col_name: str = "Name") -> dict:
    camarrons: pd.DataFrame = get_camas(config)
    result = dict(
        [(v[col_name], v) for k, v in camarrons.transpose().to_dict().items()]
    )
    return result


def col_index_to_sheets_col_name(idx: int) -> str:
    """
    >>> col_index_to_sheets_col_name(28)
    'AC'
    >>> col_index_to_sheets_col_name(94)
    'CQ'
    >>> col_index_to_sheets_col_name(0)
    'A'
    """
    idx_first_letter = floor(idx / 26) - 1
    if idx_first_letter < 0:
        return ascii_uppercase[idx]

    return ascii_uppercase[idx_first_letter] + ascii_uppercase[idx % 26]


def row_index_to_sheets_row_name(idx):
    """
    >>> row_index_to_sheets_row_name(0)
    '1'
    >>> row_index_to_sheets_row_name(28)
    '29'
    """
    return str(idx + 1)


def get_sheets_coord(ii_x, ii_y):
    """
    >>> get_sheets_coord(0, 28)
    'AC1'
    """
    return f"{col_index_to_sheets_col_name(ii_y)}{row_index_to_sheets_row_name(ii_x)}"


def new_cama_data(config, name):
    creds = build_creds_from_dict(config)
    sheets_service = build("sheets", "v4", credentials=creds).spreadsheets()
    append_range = f"{TAB_NAME}!A1:D1"
    body = {
        "range": append_range,
        "majorDimension": "ROWS",
        "values": [(name, 1, "", "")],
    }
    result = (
        sheets_service.values()
        .append(
            spreadsheetId=config["SHEETS_DB_FILE_ID"],
            range=append_range,
            body=body,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
        )
        .execute()
    )

    assert 1 == result["updates"]["updatedRows"]


def update_cama_data(config, cama_name, update_dict, match_column_name="Name"):
    camas_df = get_camas(config).reset_index()
    sheet_row_index_for_cama: int = (
        camas_df[camas_df[match_column_name] == cama_name].index + 1
    )[0]
    updates: List[Tuple[str, str]] = []
    for update_key, new_value in update_dict.items():
        sheet_col_index_for_cama: int = camas_df.columns.to_list().index(update_key) - 1
        sheets_update_coord = get_sheets_coord(
            sheet_row_index_for_cama, sheet_col_index_for_cama
        )
        if new_value is not None:
            updates += [(sheets_update_coord, new_value)]

    creds = build_creds_from_dict(config)
    sheets_service = build("sheets", "v4", credentials=creds).spreadsheets()
    body = {
        "value_input_option": "USER_ENTERED",  # RAW
        "data": [
            {"range": f"'{TAB_NAME}'!{updateCell}", "values": [[update_value]]}
            for updateCell, update_value in updates
        ],
    }
    result = (
        sheets_service.values()
        .batchUpdate(spreadsheetId=config["SHEETS_DB_FILE_ID"], body=body)
        .execute()
    )

    assert len(updates) == result["totalUpdatedCells"]


def distribute_coin_to_camarron_with_name(name: str):
    config = dict(os.environ)
    camas = get_camarrons(config)
    if spend_coin("TREASURY") is True:
        if name not in camas:
            new_cama_data(config, name)
        else:
            cama = camas[name]
            cama["Coinz"] = 1 + int(cama["Coinz"])
            update_cama_data(config, name, cama)
    else:
        pass


def spend_coin(name: str):
    config = dict(os.environ)
    camas = get_camarrons(config)
    if name not in camas:
        return False

    cama = camas[name]
    if int(cama["Coinz"]) <= 0:
        return False
    cama["Coinz"] = int(cama["Coinz"]) - 1
    update_cama_data(config, name, cama)
    cama = camas["TREASURY"]
    cama["Coinz"] = int(cama["Coinz"]) + 1
    update_cama_data(config, "TREASURY", cama)

    return True

def sacrifice(name: str):
    config = dict(os.environ)
    camas = get_camarrons(config)
    if name not in camas:
        return -1
    cama = camas[name]
    if int(cama["Coinz"]) <= 0:
        return -1
    sacrifice_amt = random.randint(0, int(cama["Coinz"]))        
    cama["Coinz"] = int(cama["Coinz"]) - sacrifice_amt
    update_cama_data(config, name, cama)
    cama = camas["TREASURY"]
    cama["Coinz"] = int(cama["Coinz"]) + sacrifice_amt
    update_cama_data(config, "TREASURY", cama)

    return sacrifice_amt

def send_coin(sender: str, sendee: str):
    config = dict(os.environ)
    camas = get_camarrons(config)
    if spend_coin("TREASURY") is True:
        if sender not in camas:
            return False
        else:
            cama = camas[sender]
            if int(cama["Coinz"]) <= 0:
                return False
            cama["Coinz"] = int(cama["Coinz"]) - 1
            update_cama_data(config, sender, cama)
            if sendee not in camas:
                new_cama_data(config, sendee)
            else:
                cama = camas[sendee]
                cama["Coinz"] = int(cama["Coinz"]) + 1            
                update_cama_data(config, sendee, cama)
    return True   

def transfer_coins(sender: str, recipient: str, amt: int):
    config = dict(os.environ)
    camas = get_camarrons(config)
    if sender not in camas:
        return False
    else:
        cama = camas[sender]
        cama["Coinz"] = int(cama["Coinz"]) - amt
        update_cama_data(config, sender, cama)
        if recipient not in camas:
            new_cama_data(config, recipient)
        else:
            cama = camas[recipient]
            cama["Coinz"] = int(cama["Coinz"]) + amt           
            update_cama_data(config, recipient, cama)
        return True       


def get_balance_for_name(name: str) -> int:
    config = dict(os.environ)
    camas = get_camarrons(config)
    if name not in camas:
        return 0

    return camas[name]["Coinz"]


if __name__ == "__main__":
    print(get_balance_for_name("TREASURY"))
