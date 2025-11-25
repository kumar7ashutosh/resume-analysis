import os,json

class Promptloader:
    def __init__(self,prompts_file,logger):
        self.logger=logger
        self.prompts_file=prompts_file
        self.prompts=self._load_prompts()
    def _load_prompts(self):
        with open(self.prompts_file,'r',encoding='utf-8') as f:
            prompts=json.load(f)
            self.logger.debug('prompts loaded successfully')
        return prompts
    def get_prompt(self,prompt_key,**kwargs):
        template=self.prompts[prompt_key]['template']
        formatted_prompt=template.format(**kwargs)
        self.logger.debug('prompt fetched and formatted for key %s',prompt_key)
        return formatted_prompt
