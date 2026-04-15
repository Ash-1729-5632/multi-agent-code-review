# save this as test_api.py and run it
import httpx
import json

code = """
def divide(a, b):
    return a / b

PASSWORD = "secret123"
"""

response = httpx.post(
    "http://localhost:8000/review",
    json={"code": code, "filename": "test.py"},
    timeout=120.0  # pipeline takes ~40s
)

result = response.json()
print(f"Total issues : {result['total_issues']}")
print(f"Tokens used  : {result['total_tokens']}")
print(f"Time taken   : {result['time_taken_seconds']}s")
print(f"\nFirst issue  : {result['issues'][0]}")