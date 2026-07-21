import re
import json

test_err = """Error code: 400 - {'error': {'message': "Failed to call a function. Please adjust your prompt. See 'failed_generation' for more details.", 'type': 'invalid_request_error', 'code': 'tool_use_failed', 'failed_generation': '<function=search_hotels>{"destination": "Goa"}'}}"""

match = re.search(r"<function=(\w+)[^>]*>(\{\s*\".*?\})", test_err)
if not match:
    match = re.search(r"<function=(\w+)", test_err)

fn_name = match.group(1)
args_match = re.search(r"(\{\s*\".*?\})", test_err)
fn_args = json.loads(args_match.group(1)) if args_match else {}

print("Extracted Name:", fn_name)
print("Extracted Args:", fn_args)
