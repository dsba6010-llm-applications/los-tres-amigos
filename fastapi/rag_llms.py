import json
import os
## This is used to do any environmental set up
CONFIG = json.load(open("llm_config.json"))
openai_api_key = open(f'{CONFIG["KEY_FOLDER"]}/{CONFIG["OPENAI_API_KEY_FILE"]}').read().strip()
os.environ["OPENAI_API_KEY"] = openai_api_key