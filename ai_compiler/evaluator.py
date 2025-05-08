"""
evaluate the output of a compiled executable legitimacy
"""
import queue
from threading import Thread
import random
from openai import OpenAI
import os
import re
from ai_compiler.llm_client import llmClient


class EvalTaskConfig():
    def __init__(self, executable_id, exec_result, result_eval_prompt, should_force_check):
        self.executable_id = executable_id
        self.exec_result = exec_result
        self.result_eval_prompt = result_eval_prompt
        self.should_force_check = should_force_check

class Evaluator:
    def __init__(self):
        pass

    @classmethod
    def eval(cls, result, eval_prompt):
        print("starting eval ...")
        
        prompt = f"""
        the python file execution result is as follows:
        {result}
        is the statement below true?
        {eval_prompt}
        if the statement is true, please answer with "true", if the statement is false, please answer with "false", and nothing else, no explanation, no comments, no print statements, no markdown
        """
        print(f"prompt: {prompt}")
        response = llmClient.generate(
            prompt,
            system_prompt="you are data format inspector",
            trim_thinking=True,
            trim_code=False
        )
        response = response.lower()
        print(f"eval response: {response}")
        # check if the response is true or false
        if response == "true":
            return True
        elif response == "false":
            return False
        else:
            raise ValueError(f"unexpected response: {response}")

"""
create a thread for eval queue
"""
eval_q = queue.Queue()

def eval_loop(q):
    while True:
        eval_task_config = q.get()
        if eval_task_config.force_check or random.choice([True, False]):
            """
            check 1/2 of the results
            """
            if not Evaulator.eval(eval_task_config.exec_result, eval_task_config.result_eval_prompt):
                """
                let compile q start compile exec_id
                """
                pass
        
        q.task_done()

eval_thread = Thread(target=eval_loop, args=(eval_q,))
eval_thread.setDaemon(True)
eval_thread.start()

