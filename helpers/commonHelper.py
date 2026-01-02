
import re
from datetime import datetime
DATE_FORMAT='%d.%m.%Y'

VERBOS_LEVEL_NONE = 0
VERBOS_LEVEL_INFO = 1
VERBOS_LEVEL_DEBUG = 2

def get_verbos_level():
    return 2

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

def is_subject_ignored(subject):
    return 'pogashenie' in subject or 'neuspeshen' in subject

def create_line_object(text, id):
    # Regular expression to match BGN numbers
    #bgn_pattern = r"\b\d+(?:\.\d{1,2})?\s*BGN\b"
    bgn_pattern = r'POKUPKA\s+(\d+\.\d+)'
    
    # Regular expression to match BGN numbers
    #bgn_pattern = r"\b\d+(?:\.\d{1,2})?\s*BGN\b"
    #euro_pattern = r"\b(\d+(?:\.\d{1,2})?)\s*EUR\b"
    euro_pattern = r'\((\d+\.\d+)\s*EUR\)'

    # Regular expression to match USD numbers
    #bgn_pattern = r"\b\d+(?:\.\d{1,2})?\s*USD\b"
    usd_pattern = r"\b(\d+(?:\.\d{1,2})?)\s*USD\b"
    
    # Regular expression to match dates
    date_pattern = r"\b\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2}\b"

    # Find all BGN numbers in the text
    bgn_matches = re.findall(bgn_pattern, text)
    # print('bgn_matches: ' + ' '.join(bgn_matches))
    
    # Find all BGN numbers in the text
    eur_matches = re.findall(euro_pattern, text)
    # print('eur_matches: ' + ' '.join(eur_matches))

    usd_matches = re.findall(usd_pattern, text)
    # print('eur_matches: ' + ' '.join(eur_matches))
    
    # Find all dates in the text
    date_matches = re.findall(date_pattern, text)

    #$if not eur_matches or usd_matches:
    #   raise ValueError("No EUR value found in text")

    # if we just load we don't need this data
    if (len(eur_matches)):
        bgn_matches.clear()
        first_eur_value = float(eur_matches[0])

        # Multiply by the exchange rate
        exchange_rate = 1.95583
        result = first_eur_value * exchange_rate
        #items = re.findall(r'\d+\.\d+', (eur_matches[0] + eur_matches[0]))
        bgn_matches.append(str(result))

    if (len(usd_matches)):
        bgn_matches.clear()
        items = re.findall(r'\d+\.\d+', usd_matches[0])
        usd_value = round(float(items[0]),2) * 1.85
        bgn_matches.append(str(usd_value))
    
    comment1 = ''
    comment2 = ''

    # Return a tuple of th BGN numbers and dates
    if  (len(date_matches) and len(bgn_matches)):
        value = negativeNumber(bgn_matches[0])
        date = convert_to_date(date_matches[0])
        msg_id = date + '_' + id
        return [date, value, comment1, comment2, msg_id]
    else:
        return False
