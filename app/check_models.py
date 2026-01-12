import os
from dotenv import load_dotenv

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    print("CANT NOT FIND KEY")
    exit(1)

from google.genai import Client
from app.core.config import settings

def check_available_models():
    print(f"Check models: {settings.GOOGLE_API_KEY[:5]}...")

    try:
        client = Client(api_key=settings.GOOGLE_API_KEY)
        pager = client.models.list(config={"page_size": 50})

        print("\nModel:")
        print("-" * 40)

        count = 0
        for model in pager:
            print(f" 👉 {model.name}")
            count += 1

        if count == 0:
            print("CAN NOT FIND MODEL")
        else:
            print("-" * 40)
            print(f"ALL: {count} model.")

    except Exception as e:
        print(f"\n❌ CAN NOT CALL API: {e}")

if __name__ == "__main__":
    check_available_models()