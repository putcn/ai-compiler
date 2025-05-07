"""
evaluate the output of a compiled executable legitimacy
"""
import queue
from threading import Thread
import random


class EvalTaskConfig():
    def __init__(self, executable_id, exec_result, result_eval_prompt, should_force_check):
        self.executable_id = executable_id
        self.exec_result = exec_result
        self.result_eval_prompt = result_eval_prompt
        self.should_force_check = should_force_check

class Evaulator:
    def __init__(self):
        pass

    @classmethod
    def eval(cls, result, eval_prompt):
        return True

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

