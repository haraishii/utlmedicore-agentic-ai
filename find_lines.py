with open(r"e:\agentic\templates\agentic_interface_enhanced.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

matched = []
for i, line in enumerate(lines):
    if "generateReport" in line and "function" in line.lower():
        matched.append(f"{i+1}: {line.strip()}")

print(f"Total matched: {len(matched)}")
for m in matched:
    print(m)
