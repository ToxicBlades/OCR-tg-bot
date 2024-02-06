import os
DIRECTORY = "./data/"

def get_excel_files(directory=DIRECTORY,delimiter='\n'):
    excel_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".xlsx"):
            excel_files.append(filename)
    return delimiter.join(excel_files)


