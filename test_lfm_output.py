import ollama

try:
    prompt = "Extract entities and edges from this text in JSON form: 'Patient is Sitting with HR 80 and Normal condition'."
    resp = ollama.chat(model="lfm2.5-thinking:1.2b", messages=[{"role": "user", "content": prompt}])
    print("--- LFM2.5 OUTPUT ---")
    print(resp['message']['content'])
    print("--------------------")
except Exception as e:
    print("Error calling LFM2.5:", e)
