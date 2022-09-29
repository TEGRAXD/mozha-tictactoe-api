from app import app
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
    app.run(host=os.environ.get("HOST"), port=os.environ.get("PORT"))