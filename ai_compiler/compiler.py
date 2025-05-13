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
import re
from ai_compiler.evaluator import Evaluator
from ai_compiler.llm_client import llmClient
import random
import requests


def get_url_content(url:str)->str:
    headers_list=[
        {"accept-language": "en-US,en;q=0.9","accept-encoding": "gzip, deflate, br","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36","accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"},
        {"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6","accept-encoding": "gzip, deflate, br, zstd","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36","accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}
    ]

    headers = random.choice(headers_list)
    resp = requests.get(url, headers=headers)
    if(resp.status_code != 200):
        return None
    return resp.text

class Compiler:
    def __init__(self, executable_id):
        self.executable_id = executable_id

    def _gen_python_exec(self, exec_config, previous_executable=None, previous_exec_result=None):
        
        pip_packages = [
            "beautifulsoup4",
            "requests",
            "scrapy",
        ]

        example_url_content = get_url_content("https://www.amazon.com/dp/B013J7O3X0")


        prompt = f"""
        the python file generation instruction is as follows:
        the python file execution environment has the following pip packages installed:
        {pip_packages}
        this python file reads the following environment variables as input:
        {exec_config["env_variables"]}
        there is a utility function called get_url_content(url:str)->str you can import with 'from amazon_utils import get_url_content', with which you can use to get the amazon page html page content, if it returns None, it means the http request failed. the example page content is as follows:
        {example_url_content}

        the python file is to do the following task:
        {exec_config["python_gen_prompt"]}
        this python files result is output to stdout, and the result is a json string in the following example format:
        {exec_config["result_example"]}
        make sure you only output the plain python file, and nothing else, no explanation, no comments, no print statements, no markdown, wrap the code in markdown python code block
        """
        if previous_executable is not None and previous_exec_result is not None:
            prompt += f"""
            the previous python file is as follows:
            {previous_executable}

            the previous python file execution result is as follows:
            {previous_exec_result}

            the new python file should be generated based on the previous python file and its execution result, if there is any error in the previous python file, please fix it, and if there is any error in the previous python file execution result, please fix it, and if there is no error in the previous python file and its execution result, please generate a new python file based on the previous python file and its execution result
            """
        print(f"prompt: {prompt}")
        response = llmClient.generate(
            prompt, 
            system_prompt="you are a python file generator, you generate a single execuable python file as instructed", 
            trim_thinking=True,
            trim_code=True
        )

        print(f"python file content: {response}")
        return response

    def compile_once(self, exec_config, previous_executable=None, previous_exec_result=None):
        
        
        python_file_str = self._gen_python_exec(exec_config, previous_executable, previous_exec_result)
        with tempfile.TemporaryDirectory(delete=False) as temp_dir:
            """
            step 1: create python exec file in temp file folder
            """
            temp_py_file_path = os.path.join(temp_dir, "main.py")
            with open(temp_py_file_path, "w") as temp_py_file:
                temp_py_file.write(python_file_str)
        
            print(f"python file created at {temp_py_file_path}")
            """
            step2: create docker file in temp folder
            """

            docker_file_str = f"""
            FROM ai_compiler_base:latest
            COPY main.py /app/main.py
            WORKDIR /app
            CMD ["python", "main.py"]
            """
            temp_dockerfile_path = os.path.join(temp_dir, "Dockerfile")
            with open(temp_dockerfile_path, "w") as temp_docker_file:
                temp_docker_file.write(docker_file_str)
            print(f"docker file created at {temp_dockerfile_path}")

       
            """
            step3: build docker image
            """
            print("building docker image...")
            docker_client = docker.DockerClient(base_url=os.getenv("DOCKER_BASE_URL"))
            docker_client.images.build(
                path=temp_dir,
                dockerfile=temp_dockerfile_path,
                tag=self.executable_id,
                rm=True,
            )
            print(f"docker image {self.executable_id} built")
       
        return python_file_str
    
    def compile(self, exec_config):
        docker_client = docker.DockerClient(base_url=os.getenv("DOCKER_BASE_URL"))
        print(f"compiling {self.executable_id}...")
        previous_exec_result = None
        previous_executable = None
        eval_result = False
        while not eval_result:
            print("previous eval not pass, recompiling...")
            previous_executable = self.compile_once(exec_config, previous_executable, previous_exec_result)
            print("python code generated, start test run...")
            try:
                previous_exec_result = docker_client.containers.run(
                    self.executable_id,
                    environment=exec_config["testing_parameters"],
                )
            except docker.errors.ContainerError as e:
                print(f"docker container run error: {e}")
                previous_exec_result = e.stderr.decode("utf-8")
            except Exception as e:
                print(f"docker container run error: {e}")
                previous_exec_result = str(e)
            print(f"test run finished, result: {previous_exec_result}")
            
            eval_result = Evaluator.eval(
                previous_exec_result,
                exec_config["result_eval_prompt"],
            )
            print("eval finished, result: ", eval_result)
        
        