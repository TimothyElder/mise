import pandas as pd
# from nltk.tokenize import sent_tokenize, word_tokenize

import logging
logger = logging.getLogger(__name__)

def documentTokenizer(text: str, granularity: str = "sentence") -> pd.DataFrame:
    """
    Tokenizes a given text into sentences or words and returns a DataFrame.

    Args:
        text (str): The text to be tokenized.
        granularity (str): Granularity level for tokenization ("sentence" or "word").

    Returns:
        pd.DataFrame: A DataFrame with 'index', 'tokens', and 'Codes' columns.
    """
    # Validate input
    if not isinstance(text, str):
        raise TypeError("Text must be of type str.")
    if not text.strip():
        raise ValueError("Text must not be empty or whitespace.")
    if granularity not in ["sentence", "word"]:
        raise ValueError('Granularity must be "sentence" or "word".')

    # Tokenize text based on granularity
    if granularity == "sentence":
        tokens = sent_tokenize(text)
    else:
        tokens = word_tokenize(text)

    # Construct the DataFrame
    data = {
        'index': list(range(len(tokens))),
        'tokens': tokens,
        'Codes': [[] for _ in range(len(tokens))]
    }
    return pd.DataFrame(data)