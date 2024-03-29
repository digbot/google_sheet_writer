from helpers.storeHelper import store_sheet_and_git_id

def get_sheet(sheet_id, sheet_title, sheets_service, client):
    if sheet_id:
        sheet = client.open_by_key(sheet_id)
    else:
        sheet_title = sheet_title
        sheet = sheets_service.spreadsheets().create(
            body={
                'properties': {'title': sheet_title},
                'sheets': [{'properties': {'title': sheet_title}}],
            }
        ).execute()
        sheet_id = sheet['spreadsheetId']
        print(f'Created new sheet with title "{sheet_title}" and ID "{sheet_id}"')
        store_sheet_and_git_id(sheet_id, sheet_title)
    return sheet

def get_first_empty_row(service, spreadsheet_id, sheet_name):
    # Get the sheet by name
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    sheet_id = None
    for sheet in sheets:
        if sheet['properties']['title'] == sheet_name:
            sheet_id = sheet['properties']['sheetId']
            break
    if not sheet_id:
        print(f"No sheet with name {sheet_name} found.")
        return None

    # Get the values in the sheet
    range_name = f"{sheet_name}!A1:Z"
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    # Find the first empty row
    row_num = len(values) + 1
    for row in values:
        if not any(row):
            return row_num
        row_num += 1
    return row_num

def get_sheet_by_name(service, spreadsheet_id, sheet_name):
    # Get the sheet by name
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    sheet = None
    for sheet in sheets:
        if sheet['properties']['title'] == sheet_name:
            return sheet
    if sheet is None:
        print(f"No sheet with name {sheet_name} found.")
        return None

def clear_worksheet(service, spreadsheet_id, sheet_name):
    sheet = get_sheet_by_name(service, spreadsheet_id, sheet_name)
    if  sheet is not None: 
        sheet.clear()
        print(f"Clearing worksheet DONE")
    else:
        print(f"Clearing worksheet SKIPED!")
      
