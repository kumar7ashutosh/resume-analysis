import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    groq_api_key=os.getenv('GROQ_API_KEY')
    log_dir='data/logs'
    prompts_file='data/prompts.json'
    
    @staticmethod
    def validate():
        if not Config.groq_api_key:
            print('api key not in environment')
            raise ValueError('api key is not set in .env file')
        
