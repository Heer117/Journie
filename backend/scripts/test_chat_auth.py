import httpx

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2YTQ4ZTQ2ZTUwOTcwZDQ2MWYzODQ0MDciLCJleHAiOjE3ODM3NjY3NjZ9.U8e93QwidX7KHIrAFi3LpoeGE_ENZP_QetNNHOqIVb4"

response = httpx.post(
    "http://127.0.0.1:8000/chat/",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={"message": "hi"},
)

print("Status code:", response.status_code)
print("Response:", response.json())