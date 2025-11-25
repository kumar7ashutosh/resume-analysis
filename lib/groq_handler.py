from groq import Groq
from utils.config import Config

class GroqHandler:
    def __init__(self,logger,prompt_loader):
        self.logger=logger
        self.prompt_loader=prompt_loader
        Config.validate()
        self.client=Groq(api_key=Config.groq_api_key)

    def analyze_text(self,prompt,text,model='gemma2-9b-it',max_tokens=2000,temperature=0):
        max_length=5000
        chunks=[text[i:i+max_length]for i in range(0,len(text),max_length)]
        partial_responses=[]
        for chunk in enumerate(chunks):
            response=self.client.chat.completions.create(
                messages=[{'role':'user','content':prompt+'\n\n'+chunk}],
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            partial_responses.append(response.choices[0].message.content.strip())
        
        if len(partial_responses)>1:
            combine_prompt = self.prompt_loader.get_prompt("combine_partial_responses")
            combined_text = "\n\n".join(partial_responses)
            final_response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": combine_prompt + "\n\n" + combined_text}],
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            result = final_response.choices[0].message.content.strip()
        else:
            result=partial_responses[0]
            
        return result