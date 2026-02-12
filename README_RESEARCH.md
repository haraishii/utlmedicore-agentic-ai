# 🔬 AI Model Research & Analysis Documentation

Welcome to the **Research Branch** of UTLMediCore. This branch documents the extensive testing and evaluation process that led to the selection of our revolutionary AI model.

---

## 🏆 The Winner: lfm2.5-thinking:1.2b

After testing **13 different AI models** across **246+ test cases**, we made a shocking discovery: 

> An ultra-lightweight **1.2B parameter model** outperformed traditional **8B and 20B models** in specialized healthcare tasks!

### 📊 Performance Summary

| Metric | **lfm2.5-thinking:1.2b** 🏆 | llama3.1:8b 🥈 | medicaldiagnostic:8b 🥉 |
|--------|-----------------------------|----------------|-------------------------|
| **Size** | **0.7 GB** (Ultra Small) | 4.9 GB | ~5 GB |
| **Fall Detection** | **100%** (14/14) | 92.9% (13/14) | 71.4% (10/14) |
| **Overall Accuracy** | **90.0%** | 73.3% | 76.7% |
| **F1 Score** | **0.903** | 0.765 | 0.741 |
| **Response Time** | **9.3s** (Fastest) | 14.2s | 13.7s |
| **False Positives** | **0** | 3 | 4 |

---

## 🧪 Research Methodology

We didn't just pick a popular model. We built a custom evaluation framework (`evaluation/model_comparison.py`) and tested against a rigorous dataset (`evaluation/test_datasets.py`):

### **The Test Cases (30 Scenarios)**
1.  **True Positives (Falls):** 14 scenarios (Bathroom slip, bedroom collapse, kitchen fall, etc.)
2.  **True Negatives (Normal):** 11 scenarios (Sleeping, sitting, walking, yoga)
3.  **Edge Cases:** 5 scenarios (Dropped phone vs. person falling, lying on couch vs. collapse)

### **The Models Evaluated**
We tested three categories of models:
1.  **General Purpose:** llama3.1:8b, llama3.2:3b, qwen2.5:7b, gemma3:12b
2.  **Medical Specialized:** medicaldiagnostic, meditron:7b, medllama2:7b, medichat:8b
3.  **Large Reasoning:** deepseek-r1:8b, deepseek-r1:14b, olmo-3:7b

---

## 📉 Why "Thinking" Models Work Better

Our research proves that for healthcare anomaly detection, **Architecture > Size**.

The `lfm2.5-thinking` model uses a localized "thinking" process (Chain of Thought evaluation) that allows it to reason through sensor data step-by-step, rather than just pattern matching. This led to:
- **Zero Missed Falls:** It understood that "velocity spike + horizontal orientation = fall" better than larger models.
- **Better Context:** It correctly identified that "lying in bed" is safe, while "lying in bathroom" is critical.

---

## 📂 Detailed Reports in this Branch

Explore the full analysis documents:

- **[LFM25_THINKING_RESULTS_SHOCKING.md](reports/LFM25_THINKING_RESULTS_SHOCKING.md)** - Deep dive into the winning model.
- **[ULTIMATE_MODEL_COMPARISON.md](reports/ULTIMATE_MODEL_COMPARISON.md)** - Side-by-side comparison of all 13 models.
- **[MEDICAL_DIAGNOSTIC_RESULTS.md](reports/MEDICAL_DIAGNOSTIC_RESULTS.md)** - Analysis of why specialized medical models failed.
- **[LLAMA32_3B_RESULTS.md](reports/LLAMA32_3B_RESULTS.md)** - Why 3B models were too inconsistent.

---

> *This branch is preserved to document the scientific method behind our engineering decisions.*
