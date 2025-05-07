"""
compile a llm instruction into a executable

example exec_config file:

{
    "state": ExecutableState
    "env_variables": list[str]
    "python_gen_prompt": str
    "result_eval_prompt": str
    "testing_parameters": dict
    "result_example": json_str
    "last_compile_time": timestamp
}
"""

import docker
from openai import OpenAI
import tempfile
import os
from runner import Runner

class Compiler:
    def __init__(self, executable_id):
        self.executable_id = executable_id

    def _gen_python_exec(self, exec_config):
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("BASE_URL"),
        )
        pip_packages = [
            "beautifulsoup4",
            "requests",
        ]
        prompt = f"""
        the python file generation instruction is as follows:
        the python file execution environment has the following pip packages installed:
        {pip_packages}
        this python file reads the following environment variables as input:
        {exec_config["env_variables"]}
        the python file is to do the following task:
        {exec_config["python_gen_prompt"]}
        this python files result is output to stdout, and the result is a json string in the following example format:
        {exec_config["result_example"]}
        """
        result = client.chat(
            messages=[
                {"role": "user", "content": prompt},
                {"role": "system", "content": "you are a python file generator, you generate a single execuable python file as instructed"},
            ],
            temperature=0.7
        )
        return result["choices"][0]["message"]["content"]

    def compile(self, exec_config):
        """
        step 1: create python exec file in temp file folder
        """
        
        python_file_str = self._gen_python_exec(exec_config)
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file.write(python_file_str.encode())
            temp_file_path = temp_file.name
        
        """
        step2: create docker file in temp file folder
        """

        docker_file_str = f"""
        FROM ai_compiler_base:latest
        COPY {temp_file_path} /app/main.py
        WORKDIR /app
        CMD ["python", "main.py"]
        """
        with tempfile.NamedTemporaryFile(suffix=".Dockerfile", delete=False) as temp_file:
            temp_file.write(docker_file_str.encode())
            docker_file_path = temp_file.name
        
        """
        step3: build docker image
        """

        docker_client = docker.from_env(base_url=os.getenv("DOCKER_BASE_URL"))
        docker_client.images.build(
            path=os.path.dirname(docker_file_path),
            dockerfile=os.path.basename(docker_file_path),
            tag=self.executable_id,
            rm=True,
        )

        """
        step4: remove temp files
        """
        os.remove(temp_file_path)
        os.remove(docker_file_path)
        
        """
        step5: run and evaluate the docker image
        """
        runner = Runner(self.executable_id)
        runner.run(exec_config["testing_parameters"])
