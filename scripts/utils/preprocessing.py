import re
import string

def clean_text(text):
    """
    Minimal cleaning to preserve urgency and authority cues.
    - Lowercase (optional, but usually good for baseline)
    - Remove extra whitespaces
    - Keep punctuation (often carries urgency like !!!)
    """
    if not isinstance(text, str):
        return ""
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # We consciously do NOT remove punctuation or stopwords here 
    # because words like "URGENT", "Now", "CEO", "!!!" are critical features.
    
    return text

def preprocess_dataframe(df, text_col='text'):
    """
    Apply cleaning to the dataframe.
    """
    df = df.copy()
    df[f'cleaned_{text_col}'] = df[text_col].apply(clean_text)
    return df
