# from ai_compiler.runner import Runner
from ai_compiler.compiler import Compiler

example_exec_config = {
    "python_gen_prompt": "use PRODUCT_ID from env variable to create a amazon product url, get the content of the page, and extract the product name, price, and rating from the page. try to mimic the human behavior, like a human visiting that page via browser, and get the content of the page. make sure the result is a json string with product name, price, and rating, values should be meaningfull values, can not be emplty, n/a or all 0.",
    "env_variables": [
        "PRODUCT_ID"
    ],
    "testing_parameters": {
        "PRODUCT_ID": "B08YQG1QB6"
    },
    "result_eval_prompt": "make sure the result is a json string with product name, price, and rating, values should be meaningfull values, can not be emplty, n/a or all 0. if it's not valid, just return false",
    "result_example": "{\"product_name\": \"example product\",\"price\": 19.99,\"rating\": 4.5}"
}

def test_runner():
    runner = Runner("amazon_scraper", example_exec_config)
    print(runner.run({
        "PRODUCT_ID": "B08YQG1QB6"
    }))

def test_compiler_prompt():
    compiler = Compiler("amazon_scraper")
    print(compiler._gen_python_exec(example_exec_config))

def test_compiler():
    compiler = Compiler("amazon_scraper")
    print(compiler.compile(example_exec_config))

if __name__ == "__main__":
    # test_runner()
   # test_compiler_prompt()
   test_compiler()