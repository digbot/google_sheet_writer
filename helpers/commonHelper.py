
import re

def extract_bgn_numbers_and_dates(text):
    result = []
    # Regular expression to match BGN numbers
    bgn_pattern = r"\b\d+(?:\.\d{1,2})?\s*BGN\b"
    
    # Regular expression to match dates
    date_pattern = r"\b\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2}\b"

    # Find all BGN numbers in the text
    bgn_matches = re.findall(bgn_pattern, text)
    
    # Find all dates in the text
    date_matches = re.findall(date_pattern, text)

    # Return a tuple of th BGN numbers and dates
    if  (len(date_matches) and len(bgn_matches)):
        return [date_matches[0], bgn_matches[0]]
    else:
        return False