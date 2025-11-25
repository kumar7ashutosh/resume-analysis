class ResumeAnalyzer:
    def __init__(self,groq_handler,logger,prompt_loader):
        self.grok=groq_handler
        self.logger=logger
        self.prompt_loader=prompt_loader
    
    def analyze_resume(self,text,designation,experience,domain):
        prompt=self.prompt_loader.get_prompt(
            'resume_analysis',
            designation=designation,
            experience_level=experience,
            domain=domain
        )
        result=self.grok.analyze_text(prompt,text,max_tokens=3000)
        return result