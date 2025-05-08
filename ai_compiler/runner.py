"""
attemp to run the compiled executable, if not ready, request to compile and wait until it's ready and run the executable again.

example exec_config file:

{
    "state": ExecutableState
    "python_gen_prompt": str
    "env_variables": list[str]
    "result_eval_prompt": str
    "result_exampe": json_str
    "last_compile_time": timestamp
}
"""

from enum import Enum
import docker
import dotenv
import os
import json
from ai_compiler.evaluator import eval_q, EvalTaskConfig
import time
from compiler import Compiler

dotenv.load_dotenv()

class ExecutableState(Enum):
    NOT_CREATED = 0
    COMPILEING = 1
    READY = 2

class Runner:
    def __init__(self, executable_id: str, exec_config: dict = None):
        self.executable_id = executable_id
        if exec_config is not None:
            self.exec_config = exec_config
            self._save_exec_config()
        else:
            self.exec_config = self._retrive_exec_config()

    def run(self, parameters: dict, should_force_eval: bool = False) -> str:
        if self._check_executable_state() is not ExecutableState.READY:
            self._recompile()
        docker_client = docker.from_env(base_url=os.getenv("DOCKER_BASE_URL"))
        exec_result = docker_client.containers.run(self.executable_id, environment=parameters)
        """
        need to deal with exceptions here
        """
        eval_task_config = EvalTaskConfig(
            self.executable_id, exec_result, self._retrive_exec_config()["result_eval_prompt"], should_force_eval
        )
        eval_q.put(eval_task_config)
        return exec_result
    
    def _check_executable_state(self) -> ExecutableState:
        config = self._retrive_exec_config()
        return config.state
    
    def _get_config_file_path(self):
        return os.getenv("CONFIG_FILE_PATH_BASE") + "/" + self.executable_id + ".json"
    
    def _retrive_exec_config(self) -> dict:
        """
        try to access the config file and return the json content
        """
        config_file_path = self._get_config_file_path()
        if not os.path.exists(config_file_path):
            return {
                "state": ExecutableState.NOT_CREATED
            }
        else:
            with open(config_file_path, "r") as conf_file:
                return json.load(conf_file)
    def _save_exec_config(self):
        with open(self._get_config_file_path()) as config_file:
            json.dump(self.exec_config, config_file)

    def _recompile(self):
        config = self.exec_config
        config.update({
            "state": ExecutableState.COMPILEING,
            "last_compile_time": time.time()
        })
        self._save_exec_config()
        compiler = Compiler(self.executable_id)
        compiler.compile(config)
        self.run(config["testing_parameters"], should_force_eval=True)
        config["state"] = ExecutableState.READY
        self._save_exec_config()