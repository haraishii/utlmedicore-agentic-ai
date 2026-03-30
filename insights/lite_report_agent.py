"""
Lite Agentic Report Generator - PRO VERSION
Forced Correlation & Clinical Insights Engine
"""

import json
from textwrap import dedent

def generate_lite_narrative(patient_id, vital_signs, activities, locations, nutrition, alerts, risk_score, graphiti_summary, time_range_hours, model_caller, manual_context=None):
    """
    Advanced Multi-Step Analysis:
    1. Correlation Analyst: Finds "WHY" things happen.
    2. Senior Medical Writer: Translates findings into professional advice.
    """
    
    # Build manual context text
    manual_logs_text = "No manual logs recorded."
    has_manual = False
    if manual_context:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
        from utils.tz_utils import utc_to_utc8
        lines = []
        for entry in manual_context:
            ts = utc_to_utc8(entry.get('timestamp', ''))
            cat = entry.get('name', 'unknown')
            if cat.startswith('meal'): cat = 'MEAL'
            elif cat.startswith('activity'): cat = 'ACTIVITY'
            elif cat.startswith('medical'): cat = 'MEDICAL RECORD'
            lines.append(f"- [{ts} UTC+8] [{cat}] {entry.get('content', '')}")
        manual_logs_text = "\n".join(lines)
        has_manual = True
    
    # Context Construction
    raw_data = dedent(f'''
        PATIENT ID: {patient_id}
        MONITORING DURATION: {time_range_hours} hours
        
        VITALS: {json.dumps(vital_signs, indent=2)}
        PHYSICAL ACTIVITIES: {json.dumps(activities, indent=2)}
        LOCATION LOGS: {json.dumps(locations, indent=2)}
        NUTRITION: {json.dumps(nutrition, indent=2)}
        SYSTEM ALERTS: {json.dumps(alerts, indent=2)}
        
        GRAPH MEMORY (Contextual Trends):
        {graphiti_summary}
        
        MANUAL PATIENT LOGS (Meals, Activities, Medical Records):
        {manual_logs_text}
    ''').strip()

    # Build manual-specific analysis instructions
    manual_analysis_instruction = ""
    if has_manual:
        manual_analysis_instruction = dedent("""
        6. MANDATORY - MANUAL MEAL LOG ANALYSIS: The patient has provided self-reported meal logs. You MUST:
           a) List EACH logged meal BY NAME (e.g. "nasi goreng", "fried chicken with cabbage", "banana") and estimate its nutritional impact.
           b) For each meal, check if the heart rate or SpO2 changed within 30-60 minutes after that meal timestamp.
           c) If meals are high-calorie or high-sodium, flag this as a dietary concern with specific reasoning.
           d) Summarize the patient's daily eating pattern (meal timing, frequency, variety).
        7. MANDATORY - MANUAL ACTIVITY LOG ANALYSIS: The patient has also reported activity logs. You MUST:
           a) List EACH logged activity BY DESCRIPTION and TIME (e.g. "woke up from sleep at 07:59", "sitting at laptop working for 2 hours at 14:29").
           b) For each activity, check if the sensor posture data (Lying, Sitting, etc.) matches what the patient reported at that timestamp.
           c) Analyze the patient's sleep-wake cycle based on reported sleep/wake entries.
           d) Assess if the patient's daily routine includes enough physical movement or is too sedentary.
           e) Note any discrepancy between self-reported activities and sensor-detected posture.
        """).strip()
    else:
        manual_analysis_instruction = "6. Note that no manual logs were provided. Recommend the patient start logging meals and activities for better analysis."

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
        5. Does the Calorie Burned (Energy Expenditure) align with the activity level? 
           NOTE: If Calorie Intake is 0, it means it hasn't been logged via sensor; check Manual Logs for actual meals.
        {manual_analysis_instruction}
        
        Be critical. If the data looks inconsistent (like high steps but mostly sitting), point it out as a sensor error or a specific health concern.
        Provide your analysis in sharp, bulleted points. Reference specific meals, times, and activities by name.
    ''').strip()

    try:
        print(f"[LITE AGENT] Starting Correlation Analysis for {patient_id}...")
        if has_manual:
            print(f"[LITE AGENT] Manual context included: {len(manual_context)} entries")
        raw_analysis = model_caller(analyst_prompt)
    except Exception as e:
        print(f"[LITE AGENT] Phase 1 Failed: {e}")
        raw_analysis = f"Data correlation failed: {str(e)}"

    # Build manual-specific writing instructions
    manual_writing_instruction = ""
    if has_manual:
        manual_writing_instruction = dedent(f"""
        CRITICAL RULE - MANUAL LOGS INTEGRATION:
        The patient has self-reported the following logs. You MUST directly reference them in your report:
        {manual_logs_text}
        
        ALL timestamps above are in UTC+8 (patient's local timezone). Use these times as-is in your report.
        
        - In "Dietary and Lifestyle Assessment": 
          * Mention EACH meal by its actual name and time.
            Example: "At 12:23, the patient ate rice with fried chicken and cabbage (~700 kcal)."
          * Mention EACH activity log by description and time.
            Example: "At 07:59, the patient woke up from sleep. At 14:29, they reported sitting at their laptop working for 2 hours."
          * Analyze the sleep-wake pattern from activity logs.
          * Assess if the daily routine includes enough movement.
        - In "Expert Recommendations": Base at least 2 recommendations on the actual meals AND activities logged.
          Example meal rec: "Consider shifting the nasi goreng dinner to before 20:00 for better digestive rest."
          Example activity rec: "After 2 hours of sitting at the laptop, take a 5-minute walk to improve circulation."
        - Do NOT say "no manual logs available" or "encourage logging" — the logs ARE available and listed above.
        - Do NOT use UTC times. All times in your report must be the UTC+8 times shown above.
        """).strip()

    # --- PHASE 2: THE CLINICAL WRITER ---
    writer_prompt = dedent(f'''
        You are a Chief Medical Officer writing a professional health report.
        Convert the following internal analysis into a clear, professional health report for a family caregiver.
        
        INTERNAL ANALYSIS:
        {raw_analysis}
        
        {manual_writing_instruction}
        
        REPORT REQUIREMENTS:
        - TONE: Professional, authoritative, compassionate. Written like a real medical report.
        - NO EMOJIS: Do not use any emoji characters anywhere in the report. Use plain text only.
        - NO REPEATING: Do not just list the numbers. Explain what they MEAN for the patient's health.
        - CORRELATION: Explicitly mention patterns between meals, activities, locations and vital signs.
        - RECOMMENDATIONS: Provide 3-5 SPECIFIC, ACTIONABLE steps based on the actual data and meals logged.
        
        STRUCTURE (Use Markdown, NO emojis in headings):
        # Clinical Health Executive Summary
        [1 paragraph professional summary. If meals were logged, mention the dietary pattern here.]
        
        ## Analytical Insights and Pathophysiology
        [Discuss correlations between sensor data and manual logs. Reference specific meals and activities.]
        
        ## Dietary and Lifestyle Assessment
        [Analyze the patient's logged meals and activities. Mention each meal by name, time, and estimated caloric impact. Assess meal timing and nutritional balance.]
        
        ## Risk and Anomaly Detection
        [Mention data inconsistencies, sensor issues, or health risks. Include dietary risks if applicable.]
        
        ## Expert Recommendations
        - [Specific Action 1 - based on actual data]
        - [Specific Action 2 - based on actual meals/activities logged]
        - [Specific Action 3 - based on sensor anomalies]
        - [Specific Action 4 - lifestyle improvement]
    ''').strip()

    try:
        print(f"[LITE AGENT] Crafting Final Narrative for {patient_id}...")
        final_narrative = model_caller(writer_prompt)
        return final_narrative
    except Exception as e:
        print(f"[LITE AGENT] Phase 2 Failed: {e}")
        return f"Report writing failed: {str(e)}"
