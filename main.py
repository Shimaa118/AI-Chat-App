# main.py
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")


from backend.routes import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
