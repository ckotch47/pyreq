import os
import re
import yaml
from dotenv import load_dotenv

load_dotenv()

def replace_env_vars(text):
    pattern = r'\$\{([^}]+)\}'

    def replace_match(match):
        var_name = match.group(1) or match.group(2)
        value = os.getenv(var_name)
        if not value:
            return
        if any(c in value for c in ' :@#{}[],'):
            value = f'"{value}"'
        return value

    return re.sub(pattern, replace_match, text)

def load_and_resolve_env(path):
    yaml_content = open(path, "r", encoding="utf-8").read()
    resolved_content = replace_env_vars(yaml_content)
    try:
        config = yaml.safe_load(resolved_content)
        return config
    except yaml.YAMLError as e:
        print("YAML невалидный:", e)