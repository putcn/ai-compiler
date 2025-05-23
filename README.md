The AI-Compiler project is inspired by the challenges of maintaining web crawlers on platforms like Apify.com, where many crawlers become obsolete. In theory, repairing these crawlers (e.g., adjusting CSS selectors when webpage HTML structures change) should be straightforward. However, without proactive monitoring, failures persist. AI could automate this process by periodically validating crawler outputs and self-correcting errors through iterative code adjustments.

Furthermore, many light and deterministic tasks currently handled by LLMs (e.g., formatting structured data) could instead be compiled into AI-generated Python scripts or even binaries and run them instead, reducing computational overhead.

LLM coding may not be the silver bullet for all tasks, but if we focus on specific use cases, we can still make things more efficient and need less human effort.

![alt text](image.png)

Current Implementation
The system:

Generates Python code from user prompts

Packages it into Docker containers

Runs test data validation

Recompiles with error feedback until validation succeeds

Key Issue: The compilation falls in to the compile, not passing evaluation, recompile loop. My guess is: LLMs (tested with local Qwen-32B and OpenAI's GPT-4o) modify code randomly without understanding root causes. Only with the validation output is not good enough for effective fixes.

May 13, 2025 Update
Revised Approach:

After thinking carefully about the code generation process, when the AI generates parsing code, it actually doesn't know what the Amazon page's HTML looks like, so the generated parsing code is completely a gussing work. Similar situations may also occur in other API request processes if the API does not provide detailed structured documentation to the AI model.

The ideal approach here is to break down the problem: 1. Ensure stable retrieval of page content; 2. Parse the page. Both of these tasks require the AI compiler to generate corresponding executable files/Docker containers. However, this would require establishing a pipeline mechanism for executable files. Setting up such a mechanism would mean turning the executable Docker into a service Docker, which brings up the issue of service isolation. At present, it doesn't seem necessary to make things so complicated.

The current simple approach is to directly write a function to fetch the Amazon page, retrieve the content during compilation, and include the page content as part of the prompt to the LLM, letting the LLM write the parsing code.

At the same time, when generating the Docker, this util function is also packaged into the Docker, so that the generated Python program can call it.

In theory, this mechanism should work, but in the local runtime environment, there is an issue with the LLM's context window length, the source html is too long, it diluted the context and prompt, if I split it into pieces and use vector searching, the retrieval is not accurate enough. There is currently no good solution for this, unless the LLM's context window can be made large enough. Project Onhold.