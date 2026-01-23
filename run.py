import sys
import os

# Add project root to path FIRST
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    try:
        import uvicorn
        print("=" * 50)
        print("Starting SafeTalk AI server...")
        print("Frontend: http://127.0.0.1:8000/app")
        print("API docs: http://127.0.0.1:8000/docs")
        print("=" * 50)
        uvicorn.run(
            "ai.server:app", 
            host="127.0.0.1", 
            port=8000, 
            reload=False  # Disable reload to avoid import issues
        )
    except Exception as e:
        print(f"[ERROR] Failed to start: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
