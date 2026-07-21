import re
import ast
import json

def parse_tool_args(err_str):
    m = re.search(r"<function=(\w+)", err_str)
    if not m:
        return None, {}
    fn_name = m.group(1)
    
    a = re.search(r"(\{.*?\})", err_str)
    if not a:
        return fn_name, {}
        
    raw_args = a.group(1).rstrip(";")
    try:
        fn_args = json.loads(raw_args)
    except Exception:
        try:
            fn_args = ast.literal_eval(raw_args)
        except Exception as pe:
            print("Parse Exception:", pe)
            fn_args = {}
            
    return fn_name, fn_args

test_cases = [
    "<function=get_weather>{'destination': 'Paris', 'date': '2026-07-21'};</function>",
    '<function=search_hotels>{"destination": "Paris"}</function>',
    '<function=get_user_trips />',
]

for test in test_cases:
    fn, args = parse_tool_args(test)
    print(f"Result -> Name: {fn}, Args: {args}")
