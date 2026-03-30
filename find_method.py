import os

search_dir = r"e:\agentic"
terms = ["get_activity_summary", "def "]

for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    if "get_activity_summary" in line and "def" in line:
                        print(f"FOUND IN {path} at line {i+1}: {line.strip()}")
            except:
                pass

print("Done Searching")
