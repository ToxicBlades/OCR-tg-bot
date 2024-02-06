import os
DIRECTORY = "./data/"

def get_excel_files(directory=DIRECTORY,delimiter='\n'):
    excel_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".xlsx"):
            excel_files.append(filename)
    return delimiter.join(excel_files)


def check_text_in_response(text_to_check, directory=DIRECTORY, delimiter='\n'):
    response = get_excel_files(directory, delimiter)
    return text_to_check in response

def format_excel_name(excel_name):
    return "./data/" + excel_name