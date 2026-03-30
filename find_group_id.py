with open(r"e:\agentic\memory\patient_memory.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "group_id" in line:
        clean = line.strip().encode('ascii', 'ignore').decode('ascii')
        print(f"Line {i+1}: {clean}")
