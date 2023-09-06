
import re
from datetime import datetime

def negativeNumber(x):
    neg = float('-' + x)
    return neg

def convert_to_date(date_time_str):
    # Convert the string to datetime object
    date_time_obj = datetime.strptime(date_time_str, '%d.%m.%Y %H:%M:%S')
    # Extract only the date portion
    date_obj = date_time_obj.date()
    # Format the date as a string
    date_str = date_obj.strftime('%d.%m.%Y')
    return date_str

def extract_bgn_numbers_and_dates(text, id):
    # Regular expression to match BGN numbers
    #bgn_pattern = r"\b\d+(?:\.\d{1,2})?\s*BGN\b"
    bgn_pattern = r"\b(\d+(?:\.\d{1,2})?)\s*BGN\b"

    # Regular expression to match dates
    date_pattern = r"\b\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2}\b"

    # Find all BGN numbers in the text
    bgn_matches = re.findall(bgn_pattern, text)
    
    # Find all dates in the text
    date_matches = re.findall(date_pattern, text)

    # Return a tuple of th BGN numbers and dates
    if  (len(date_matches) and len(bgn_matches)):
        return [convert_to_date(date_matches[0]), negativeNumber(bgn_matches[0]), id]
    else:
        return False
