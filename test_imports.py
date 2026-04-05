import sys
import os
sys.path.append(os.getcwd())
try:
    from src.delivery.web_dashboard import router
    print("SUCCESS: web_dashboard imported successfully.")
except NameError as e:
    print(f"FAILED: NameError - {e}")
except Exception as e:
    print(f"FAILED: Other Error - {e}")
