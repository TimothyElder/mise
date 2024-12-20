from mise.code_manager import CodeManager
from mise.utils.text_processing import documentTokenizer
from mise.utils.file_io import load_document
from mise.data_manager import Document

def test_coding():

    text_data = Document("Document 1", "test_files/sample.md")
    
    code_dict = CodeManager()
    code_dict.add_code("Name 1", "Descriotion 1")
    code_dict.add_code("Name 2", "Descriotion 2")
    code_dict.add_code("Name 3", "Descriotion 3")
    
    try:
        text_data.assign_code_to_segment("Name 1", segment_index = 3, code_manager = code_dict)
    
    except Exception as e:
        print(f"Failed to load DOCX: {e}")

    print(text_data.token_df)