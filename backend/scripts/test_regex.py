import re
import json

test_cases = [
    '<function=get_user_trips />',
    '<function=get_user_trips></function>',
    '<function=search_hotels{"destination": "Goa"}</function>',
    'Failed to call a function. See failed_generation: <function=get_weather{"destination": "Paris", "date": "2026-09-12"}</function>'
]

for e in test_cases:
    m = re.search(r"<function=(\w+)", e)
    if m:
        fn_name = m.group(1)
        a = re.search(r"(\{.*?\})", e)
        fn_args = json.loads(a.group(1)) if a else {}
        print(f"MATCH: name='{fn_name}', args={fn_args}")
    else:
        print("NO MATCH")
