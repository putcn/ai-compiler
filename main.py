# from ai_compiler.runner import Runner
from ai_compiler.compiler import Compiler

def test_runner():
    runner = Runner("amazon_scraper", {
        "python_gen_prompt": "use PRODUCT_ID from env variable to create a amazon product url, get the content of the page, and extract the product name, price, and rating from the page",
        "env_variables": [
            "PRODUCT_ID"
        ],
        "testing_parameters": {
            "PRODUCT_ID": "B08N5WRWNW"
        },
        "result_eval_prompt": "make sure the result is a json string with product name, price, and rating, if not, just return false",
        "result_example": "{\"product_name\": \"example product\",\"price\": 19.99,\"rating\": 4.5}"
    })
    print(runner.run({
        "PRODUCT_ID": "B08N5WRWNW"
    }))

def test_compiler_prompt():
    compiler = Compiler("amazon_scraper")
    exec_config = {
        "python_gen_prompt": "use PRODUCT_ID from env variable to create a amazon product url, get the content of the page, and extract the product name, price, and rating from the page",
        "env_variables": [
            "PRODUCT_ID"
        ],
        "testing_parameters": {
            "PRODUCT_ID": "B08N5WRWNW"
        },
        "result_eval_prompt": "make sure the result is a json string with product name, price, and rating, if not, just return false",
        "result_example": "{\"product_name\": \"example product\",\"price\": 19.99,\"rating\": 4.5}"
    }
    print(compiler._gen_python_exec(exec_config))

def test_compiler():
    compiler = Compiler("amazon_scraper")
    exec_config = {
        "python_gen_prompt": "use PRODUCT_ID from env variable to create a amazon product url, get the content of the page, and extract the product name, price, and rating from the page",
        "env_variables": [
            "PRODUCT_ID"
        ],
        "testing_parameters": {
            "PRODUCT_ID": "B002VLZ81M"
        },
        "result_eval_prompt": "make sure the result is a json string with product_name, price, and rating, if not, just return false",
        "result_example": "{\"product_name\": \"example product\",\"price\": 19.99,\"rating\": 4.5}"
    }
    print(compiler.compile(exec_config))

if __name__ == "__main__":
    # test_runner()
   # test_compiler_prompt()
   test_compiler()