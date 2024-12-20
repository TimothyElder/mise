import pytest
from mise.utils.text_processing import documentTokenizer

def test_document_tokenizer_sentence_granularity():
    text = "This is the first sentence. And here is another."
    df = documentTokenizer(text, granularity="sentence")
    
    assert len(df) == 2  # Should tokenize into 2 sentences
    assert df.iloc[0]["tokens"] == "This is the first sentence."
    assert df.iloc[1]["tokens"] == "And here is another."