import os
MODE = os.getenv("MODE", "")
if MODE == "":
    print("No MODE")
    import sys
    sys.exit()
print(f"Using MODE={MODE}")
ITERATIONS = 150_000_00