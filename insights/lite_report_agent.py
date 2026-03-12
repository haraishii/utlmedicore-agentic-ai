"""
Lite Agentic Report Generator - PRO VERSION
Forced Correlation & Clinical Insights Engine
"""

import json
from textwrap import dedent

def generate_lite_narrative(patient_id, vital_signs, activities, locations, alerts, risk_score, graphiti_summary, time_range_hours, model_caller):
    """
    Advanced Multi-Step Analysis:
    1. Correlation Analyst: Finds "WHY" things happen.
    2. Senior Medical Writer: Translates findings into professional advice.
    """
    
    # Context Construction
    raw_data = dedent(f'''
        PATIENT ID: {patient_id}
        MONITORING DURATION: {time_range_hours} hours
        
        VITALS: {json.dumps(vital_signs, indent=2)}
        PHYSICAL ACTIVITIES: {json.dumps(activities, indent=2)}
        LOCATION LOGS: {json.dumps(locations, indent=2)}
        SYSTEM ALERTS: {json.dumps(alerts, indent=2)}
        
        GRAPH MEMORY (Contextual Trends):
        {graphiti_summary}
    ''').strip()

    # --- PHASE 1: THE CORRELATION ANALYST ---
    analyst_prompt = dedent(f'''
        You are a Senior Healthcare Data Scientist. 
        Your task is to find HIDDEN CORRELATIONS in this patient's data.
        
        DATA TO ANALYZE:
        {raw_data}
        
        QUESTIONS TO ANSWER (Internal Analysis):
        1. Is there a correlation between Location and Vital Sign spikes? (e.g. HR rises when in Bathroom?)
        2. Does the activity level match the vital signs? (e.g. Is the patient "sitting" but having high HR? That's an anomaly!)
        3. Are the "Unknown Area" visits associated with any risk?
        4. What is the trend of SpO2 during different postures?
        
        Be critical. If the data looks inconsistent (like high steps but mostly sitting), point it out as a sensor error or a specific health concern.
        Provide your analysis in sharp, bulleted points.
    ''').strip()

    try:
        print(f"[LITE AGENT] Starting Correlation Analysis for {patient_id}...")
        raw_analysis = model_caller(analyst_prompt)
    except Exception as e:
        print(f"[LITE AGENT] Phase 1 Failed: {e}")
        raw_analysis = f"Data correlation failed: {str(e)}"

    # --- PHASE 2: THE CLINICAL WRITER ---
    writer_prompt = dedent(f'''
        You are a Chief Medical Officer. 
        Convert the following internal analysis into a STUNNING and HELPFUL health report for a family caregiver.
        
        INTERNAL ANALYSIS:
        {raw_analysis}
        
        REPORT REQUIREMENTS:
        - TONE: Professional, authoritative, yet compassionate.
        - NO REPEATING: Do not just list the numbers. Explain what they MEAN.
        - CORRELATION: Explicitly mention patterns (e.g., "We noticed your heart rate peaks when you are in the kitchen...").
        - RECOMMENDATIONS: Provide 3-5 SPECIFIC, ACTIONABLE steps. Not generic "monitor more".
        
        STRUCTURE (Use Markdown):
        # 🏥 Clinical Health Executive Summary
        [1 paragraph summary]
        
        ## 📊 Analytical Insights & Pathophysiology
        [Discuss correlations between activities, vitals, and locations]
        
        ## ⚠️ Risk & Anomaly Detection
        [Mention anything that looks weird or dangerous]
        
        ## 💡 Expert Recommendations
        - [Specific Action 1]
        - [Specific Action 2]
        - [Specific Action 3]
    ''').strip()

    try:
        print(f"[LITE AGENT] Crafting Final Narrative for {patient_id}...")
        final_narrative = model_caller(writer_prompt)
        return final_narrative
    except Exception as e:
        print(f"[LITE AGENT] Phase 2 Failed: {e}")
        return f"Report writing failed: {str(e)}"
