import requests

def get_llama_response(user_message):
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3",
                "messages": [
                    {"role": "user", "content": user_message}
                ],
                "stream": False  # Disable streaming to get proper JSON
            }
        )

        data = response.json()

        # Error handling
        if "error" in data:
            return f"Error from model: {data['error']}"
        if "message" not in data or "content" not in data["message"]:
            return "Unexpected response format from model."

        return data["message"]["content"]

    except Exception as e:
        return f"An error occurred: {str(e)}"
