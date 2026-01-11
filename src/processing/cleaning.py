import re
import pandas as pd
import numpy as np

def clean_text(text: str) -> str:
    """
    Removes extra whitespace, HTML tags, and special characters from text.
    Returns empty string if input is not a string.
    """
    if not isinstance(text, str):
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove special characters (keep alphanumeric and basic punctuation)
    # Adjust regex based on needs. For now, just collapsing whitespace is most critical
    # and removing obviously bad chars.
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def standardize_date(date_val) -> pd.Timestamp:
    """
    Parses a value into a pd.Timestamp.
    Returns pd.NaT if parsing fails.
    """
    if pd.isna(date_val) or date_val == "":
        return pd.NaT
    
    try:
        return pd.to_datetime(date_val)
    except Exception:
        return pd.NaT

def clean_currency(value) -> float:
    """
    Cleans currency strings (e.g. '$1,234.56') to float.
    """
    if pd.isna(value):
        return 0.0
    
    if isinstance(value, (int, float)):
        return float(value)
        
    if isinstance(value, str):
        # Remove '$', ',' and whitespace
        clean_val = re.sub(r'[$,\s]', '', value)
        try:
            return float(clean_val)
        except ValueError:
            return 0.0
            
    return 0.0
