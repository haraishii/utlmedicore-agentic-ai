"""
Enhanced Report Narrative Generator using CrewAI
Generates professional AI narratives for patient reports
"""

from crewai import Agent, Task, Crew, Process
from insights.crewai_aisuite_adapter import get_aisuite_llm
from datetime import datetime
import json

class ReportNarrativeCrew:
    """
    Generate comprehensive AI narratives for patient reports
    Uses proven lfm2.5-thinking:1.2b model via aisuite
    """
    
    def __init__(self):
        # Use your proven model
        self.llm = get_aisuite_llm(
            #model="ollama:lfm2.5-thinking:1.2b",
            model="ollamacloud:kimi-k2-thinking",
            temperature=0.3  # Slightly higher for narrative
        )
    
    def generate_narrative(self, 
                          patient_id: str,
                          vital_signs: dict,
                          activities: dict,
                          locations: dict,
                          nutrition: dict,
                          alerts: dict,
                          risk_score: float,
                          graphiti_summary: str,
                          time_range_hours: int,
                          manual_context: list = None) -> str:
        # Format manual context for agents
        manual_context_text = "No manual logs recorded."
        if manual_context:
            lines = []
            for entry in manual_context:
                ts = entry.get('timestamp', '')[:16].replace('T', ' ')
                cat = entry.get('name', 'unknown')
                if cat.startswith('meal'): cat = 'MEAL'
                elif cat.startswith('activity'): cat = 'ACTIVITY'
                elif cat.startswith('medical'): cat = 'MEDICAL RECORD'
                lines.append(f"- [{ts}] [{cat}] {entry.get('content', '')}")
            manual_context_text = "\n".join(lines)

        # Create specialized agents
        data_analyst = Agent(
            role='Healthcare Data Analyst',
            goal='Analyze patient vital signs and activity patterns',
            backstory='''Expert in analyzing patient monitoring data 
            with 15 years of experience in healthcare analytics.''',
            llm=self.llm,
            verbose=False
        )
        
        clinical_writer = Agent(
            role='Clinical Report Writer',
            goal='Create clear, actionable patient health summaries',
            backstory='''Medical writer specializing in patient reports 
            for healthcare professionals. Known for clarity and actionable insights.''',
            llm=self.llm,
            verbose=False
        )
        
        # Prepare data summary for analysis
        data_summary = f"""
PATIENT: {patient_id}
TIME PERIOD: Last {time_range_hours} hours
RISK SCORE: {risk_score} ({self._get_risk_level(risk_score)})

VITAL SIGNS:
{json.dumps(vital_signs, indent=2)}

ACTIVITIES:
{json.dumps(activities, indent=2)}

LOCATIONS:
{json.dumps(locations, indent=2)}

NUTRITION:
{json.dumps(nutrition, indent=2)}

ALERTS:
Total: {alerts.get('total_alerts', 0)}
Critical: {len(alerts.get('critical_alerts', []))}
Warnings: {len(alerts.get('warning_alerts', []))}

MEMORY INSIGHTS:
{graphiti_summary}

MANUAL PATIENT LOGS (Meals, Activities):
{manual_context_text}
"""
        
        # Task 1: Analyze the data
        analysis_task = Task(
            description=f'''
Analyze this patient's health data and manual logs to identify:
1. Overall clinical status summary.
2. Meal/Activity Analysis: Assess how manually logged meals correlate with heart rate or vitals.
3. Behavioral Trends: Do sensor postures match manual sleep/wake reports?
4. Risk Anomalies: Point out any spikes near meals or locations.

Data:
{data_summary}

Provide a structured analysis covering all correlations.
''',
            agent=data_analyst,
            expected_output='Structured health analysis with key findings'
        )
        
        # Task 2: Write narrative
        narrative_task = Task(
            description='''
Based on the analysis, write a professional patient health summary.

Format as markdown with sections:
1. **Executive Summary** (2-3 sentences)
2. **Health Status Overview**
3. **Key Findings**
4. **Recommendations** (if any concerns)

Tone: Professional, clear, actionable
Length: 300-500 words
Use emojis sparingly for readability
''',
            agent=clinical_writer,
            expected_output='Professional markdown patient report'
        )
        
        # Create crew and run
        crew = Crew(
            agents=[data_analyst, clinical_writer],
            tasks=[analysis_task, narrative_task],
            process=Process.sequential,
            verbose=False
        )
        
        try:
            print(f"[REPORT CREW] Generating narrative for {patient_id}...")
            result = crew.kickoff()
            print(f"[REPORT CREW] Narrative generated ({len(str(result))} chars)")
            return str(result)
        except Exception as e:
            print(f"[REPORT CREW] Error: {e}")
            return self._fallback_narrative(patient_id, risk_score, alerts, graphiti_summary)
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level from score"""
        if score < 0.4:
            return "LOW"
        elif score < 0.7:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _fallback_narrative(self, patient_id, risk_score, alerts, graphiti_summary):
        """Fallback narrative if CrewAI fails"""
        risk_level = self._get_risk_level(risk_score)
        
        narrative = f"""
## Executive Summary

Patient {patient_id} is currently in **{risk_level} RISK** category (score: {risk_score:.2f}).

## Health Status Overview

During the monitoring period, the patient generated {alerts.get('total_alerts', 0)} alerts, 
including {len(alerts.get('critical_alerts', []))} critical alerts.

## Memory Insights

{graphiti_summary}

## Recommendations

{'⚠️ Immediate medical attention recommended due to high risk score.' if risk_score >= 0.7 else 
 '✅ Continue routine monitoring.' if risk_score < 0.4 else
 '📊 Enhanced monitoring recommended.'}
"""
        return narrative


# Singleton
_report_crew = None

def get_report_crew():
    global _report_crew
    if _report_crew is None:
        _report_crew = ReportNarrativeCrew()
    return _report_crew
