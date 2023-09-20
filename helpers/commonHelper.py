
import re
from datetime import datetime
DATE_FORMAT='%d.%m.%Y'

def negativeNumber(x):
    neg = float('-' + x)
    return neg

def convert_to_date(date_time_str):
    # Convert the string to datetime object
    date_time_obj = datetime.strptime(date_time_str, '%d.%m.%Y %H:%M:%S')
    # Extract only the date portion
    date_obj = date_time_obj.date()
    # Format the date as a string
    date_str = date_obj.strftime(DATE_FORMAT)
    return date_str

def extract_bgn_numbers_and_dates(text, id):
    # Regular expression to match BGN numbers
    #bgn_pattern = r"\b\d+(?:\.\d{1,2})?\s*BGN\b"
    bgn_pattern = r"\b(\d+(?:\.\d{1,2})?)\s*BGN\b"
    
    # Regular expression to match BGN numbers
    #bgn_pattern = r"\b\d+(?:\.\d{1,2})?\s*BGN\b"
    euro_pattern = r"\b(\d+(?:\.\d{1,2})?)\s*EUR\b"
    
    # Regular expression to match dates
    date_pattern = r"\b\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2}\b"

    # Find all BGN numbers in the text
    bgn_matches = re.findall(bgn_pattern, text)
    print('bgn_matches: ' + ' '.join(bgn_matches))
    
    # Find all BGN numbers in the text
    eur_matches = re.findall(euro_pattern, text)
    print('eur_matches: ' + ' '.join(eur_matches))
    
    # Find all dates in the text
    date_matches = re.findall(date_pattern, text)

    # if we just load we don't need this data
    if (len(bgn_matches)):
        if (bgn_matches[1] > 7020):
            bgn_matches.clear()

    if (len(eur_matches)):
        bgn_matches.clear()
        items = re.findall(r'\d+\.\d+', (eur_matches[0] + eur_matches[0]))
        bgn_matches.append(items[0])

    # Return a tuple of th BGN numbers and dates
    if  (len(date_matches) and len(bgn_matches)):
        return [convert_to_date(date_matches[0]), negativeNumber(bgn_matches[0]), id]
    else:
        return False
