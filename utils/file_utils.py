import os

def save_text_to_file(text,output_path):
    with open(output_path,'w',encoding='utf-8') as file:
        file.write(text)
        
def remove_files(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        
