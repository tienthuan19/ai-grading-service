import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Kiểm tra xem đã có Key chưa
if "GOOGLE_API_KEY" not in os.environ:
    print("❌ LỖI: Chưa tìm thấy GOOGLE_API_KEY. Hãy kiểm tra file .env")
    exit(1)

from google.genai import Client
from app.core.config import settings

def check_available_models():
    print(f"🔑 Đang kiểm tra danh sách model với Key: {settings.GOOGLE_API_KEY[:5]}...")

    try:
        client = Client(api_key=settings.GOOGLE_API_KEY)
        # Lấy danh sách tất cả model
        pager = client.models.list(config={"page_size": 50})

        print("\n✅ Danh sách các Model khả dụng:")
        print("-" * 40)

        count = 0
        for model in pager:
            # Chỉ in tên model để tránh lỗi thuộc tính
            # Lưu ý: model.name thường có dạng 'models/gemini-1.5-flash'
            print(f" 👉 {model.name}")
            count += 1

        if count == 0:
            print("⚠️ Không tìm thấy model nào. Có thể do Key hoặc quyền truy cập.")
        else:
            print("-" * 40)
            print(f"Tổng cộng: {count} model.")

    except Exception as e:
        print(f"\n❌ Lỗi khi gọi API: {e}")

if __name__ == "__main__":
    check_available_models()