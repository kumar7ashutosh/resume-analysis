import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    groq_api_key=os.getenv('GROQ_API_KEY')
    LOG_DIR='data/logs'
    PROMPTS_FILE='data_dir/prompts.json'
    
    @staticmethod
    def validate():
        if not Config.groq_api_key:
            print('api key not in environment')
            raise ValueError('api key is not set in .env file')
        
