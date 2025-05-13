from openai import OpenAI
import dotenv
import os
import re

dotenv.load_dotenv()

class LLMClient:
    def __init__(self):
        self._openai_client = OpenAI(
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY") or "sk-",
        )
    
    def generate(self, prompt, system_prompt="", trim_thinking=True, trim_code=False, temperature=0.7,):
        result = self._openai_client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "qwq"),
            messages=[
                {"role": "user", "content": prompt},
                {"role": "system", "content": system_prompt},
            ],
            temperature=temperature
        )
        response = result.choices[0].message.content

        thinking_search = re.search(r"<think>(.*?)</think>", response, flags=re.DOTALL)
        if thinking_search:
            print(thinking_search.group(1))
        if trim_thinking:
            response = self._trim_thinking(response)
        if trim_code:
            response = self._trim_code(response)
        response = response.strip()
        return response
    
    def _trim_thinking(self, response):
        # remove <think></think> tags
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        return response
    def _trim_code(self, response):
        # remove markdown code block
        response = re.sub(r"```python(.*?)```", r"\1", response, flags=re.DOTALL)
        return response

llmClient = LLMClient()