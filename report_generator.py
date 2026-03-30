"""
Health Report Generator for UTLMediCore
Generate comprehensive patient health reports in JSON and HTML formats
"""

from datetime import datetime, timedelta
import json
from collections import Counter
import numpy as np

try:
    from insights.report_crew import get_report_crew
    CREW_AVAILABLE = True
except:
    CREW_AVAILABLE = False
    print("[REPORT] CrewAI not available, using Lite Agentic Narrative")

try:
    from insights.lite_report_agent import generate_lite_narrative
    LITE_AVAILABLE = True
except ImportError:
    LITE_AVAILABLE = False


class ReportGenerator:
    """Generate comprehensive health reports for patients"""
    
    @staticmethod
    def generate_report(patient_state, alerts, agent_logs, time_range_hours=24, graph_memory_summary="", ai_narrative="", extra_data=None, model_caller=None, manual_context=None):
        """
        Generate comprehensive health report
        
        Args:
            patient_state: PatientState object
            alerts: List of alerts for this patient
            agent_logs: Agent activity logs
            time_range_hours: Report time range in hours
            
        Returns:
            dict: Structured report data
        """
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        
        # Filter data by time range
        recent_data = []
        for d in patient_state.history:
            ts = d.get('timestamp')
            if ts:
                if isinstance(ts, datetime):
                    if ts > cutoff_time:
                        recent_data.append(d)
                else:
                    try:
                        if datetime.fromisoformat(str(ts)) > cutoff_time:
                            recent_data.append(d)
                    except:
                        recent_data.append(d)  # Include if can't parse timestamp
        
        # Combine with extra data mapped from historical source if provided
        if extra_data:
            for ed in extra_data:
                # Add if not already in recent_data (very crude deduplication based on timestamps)
                ts = ed.get('timestamp')
                if ts and not any(r.get('timestamp') == ts for r in recent_data):
                    recent_data.append(ed)
        
        recent_alerts = []
        for a in alerts:
            try:
                ts_str = a.get('timestamp', '')
                if ts_str and datetime.fromisoformat(ts_str) > cutoff_time:
                    recent_alerts.append(a)
            except:
                pass
        
        recent_logs = []
        for log in agent_logs:
            try:
                ts_str = log.get('timestamp', '')
                if ts_str and datetime.fromisoformat(ts_str) > cutoff_time:
                    recent_logs.append(log)
            except:
                pass
        
        report = {
            'metadata': ReportGenerator._generate_metadata(
                patient_state.device_id, 
                time_range_hours
            ),
            'vital_signs': ReportGenerator._analyze_vitals(recent_data),
            'activity_summary': ReportGenerator._analyze_activities(recent_data),
            'location_analysis': ReportGenerator._analyze_locations(recent_data),
            'nutritional_analysis': ReportGenerator._analyze_calories(recent_data),
            'alerts_summary': ReportGenerator._summarize_alerts(recent_alerts),
            'agent_activity': ReportGenerator._summarize_agent_logs(recent_logs),
            'risk_assessment': {
                'current_risk_score': patient_state.risk_score,
                'risk_level': ReportGenerator._get_risk_level(patient_state.risk_score)
            },
            'graph_memory_summary': graph_memory_summary,
            'ai_narrative': ai_narrative,
            'data': recent_data if recent_data else []  # Provide raw records for Daily Data UI
        }
        
        # ========== GENERATE AI NARRATIVE ==========
        if not ai_narrative:
            # 1. Try Lite Agentic Narrative first (Reliable on Python 3.14, no extra deps)
            if LITE_AVAILABLE and model_caller:
                try:
                    print(f"[REPORT] Generating Lite Agentic Narrative for {patient_state.device_id}")
                    ai_narrative = generate_lite_narrative(
                        patient_id=patient_state.device_id,
                        vital_signs=report['vital_signs'],
                        activities=report['activity_summary'],
                        locations=report['location_analysis'],
                        nutrition=report['nutritional_analysis'],
                        alerts=report['alerts_summary'],
                        risk_score=patient_state.risk_score,
                        graphiti_summary=graph_memory_summary,
                        time_range_hours=time_range_hours,
                        model_caller=model_caller,
                        manual_context=manual_context
                    )
                    print(f"[REPORT] AI narrative generated via Lite Agent")
                except Exception as e:
                    print(f"[REPORT] Lite Agent failed: {e}")

            # 2. Try CrewAI as secondary (often fails on 3.14 due to dependency issues)
            if not ai_narrative and CREW_AVAILABLE:
                try:
                    print(f"[REPORT] Generating AI narrative with CrewAI for {patient_state.device_id}")
                    crew = get_report_crew()
                    ai_narrative = crew.generate_narrative(
                        patient_id=patient_state.device_id,
                        vital_signs=report['vital_signs'],
                        activities=report['activity_summary'],
                        locations=report['location_analysis'],
                        nutrition=report['nutritional_analysis'],
                        alerts=report['alerts_summary'],
                        risk_score=patient_state.risk_score,
                        graphiti_summary=graph_memory_summary,
                        time_range_hours=time_range_hours,
                        manual_context=manual_context
                    )
                    # Check if it returned the generic fallback starting with '## Executive Summary'
                    if ai_narrative and ai_narrative.strip().startswith('## Executive Summary'):
                        print(f"[REPORT] CrewAI returned generic fallback, might need better model")
                except Exception as e:
                    print(f"[REPORT] CrewAI failed: {e}")

            # 3. Final safety fallback
            if not ai_narrative:
                ai_narrative = f"### Summary for Patient {patient_state.device_id}\n\nThe patient is currently at a risk score of {patient_state.risk_score}. "
                if graph_memory_summary:
                    ai_narrative += f"\n\n**Insights:**\n{graph_memory_summary}"
        
        report['ai_narrative'] = ai_narrative
        
        return report
    
    @staticmethod
    def _generate_metadata(device_id, time_range_hours):
        """Generate report metadata"""
        now = datetime.now()
        start_time = now - timedelta(hours=time_range_hours)
        
        return {
            'device_id': device_id,
            'report_generated': now.isoformat(),
            'time_range': {
                'start': start_time.isoformat(),
                'end': now.isoformat(),
                'duration_hours': time_range_hours
            },
            'report_type': 'UTLMediCore Health Report',
            'system_version': '1.0'
        }
    
    @staticmethod
    def _analyze_vitals(data):
        """Analyze vital signs statistics"""
        if not data:
            return {
                'error': 'No data available in this time range',
                'heart_rate': {'readings_count': 0},
                'blood_oxygen': {'readings_count': 0}
            }
        
        hrs = [int(d.get('HR', 0)) for d in data if d.get('HR', 0) > 0]
        spo2s = [int(d.get('Blood_oxygen', 0)) for d in data if d.get('Blood_oxygen', 0) > 0]
        
        vitals = {
            'heart_rate': {
                'readings_count': len(hrs),
                'average': round(float(np.mean(hrs)), 1) if hrs else 0,
                'minimum': int(min(hrs)) if hrs else 0,
                'maximum': int(max(hrs)) if hrs else 0,
                'std_deviation': round(float(np.std(hrs)), 2) if hrs else 0,
                'abnormal_readings': len([hr for hr in hrs if hr < 50 or hr > 110])
            },
            'blood_oxygen': {
                'readings_count': len(spo2s),
                'average': round(float(np.mean(spo2s)), 1) if spo2s else 0,
                'minimum': int(min(spo2s)) if spo2s else 0,
                'maximum': int(max(spo2s)) if spo2s else 0,
                'hypoxia_events': len([s for s in spo2s if s < 90])
            }
        }
        
        return vitals
    
    @staticmethod
    def _analyze_activities(data):
        """Analyze activity/posture distribution"""
        # Import here to avoid circular dependency
        try:
            from agentic_medicore_enhanced import POSTURE_MAP
        except:
            POSTURE_MAP = {
                0: "Unknown", 1: "Sitting", 2: "Standing", 3: "Lying Down",
                4: "Lying on Right Side", 5: "Falling", 6: "Prone",
                7: "Lying on Left Side", 8: "Walking"
            }
        
        if not data:
            return {
                'total_readings': 0,
                'distribution': {},
                'most_common_activity': 'No data'
            }
        
        postures = []
        for d in data:
            val = d.get('Posture_state', 0)
            if isinstance(val, str) and not val.isdigit():
                postures.append(val)
            else:
                try:
                    p = POSTURE_MAP.get(int(val), 'Unknown')
                    postures.append(p)
                except ValueError:
                    postures.append('Unknown')
        
        distribution = Counter(postures)
        total = len(postures)
        
        return {
            'total_readings': total,
            'distribution': {
                posture: {
                    'count': count,
                    'percentage': round((count / total) * 100, 1)
                }
                for posture, count in distribution.most_common()
            },
            'most_common_activity': distribution.most_common(1)[0][0] if distribution else 'Unknown'
        }
    
    @staticmethod
    def _analyze_locations(data):
        """Analyze location distribution"""
        try:
            from agentic_medicore_enhanced import AREA_MAP
        except:
            AREA_MAP = {
                1: "Unknown Area", 2: "Laboratory", 3: "Corridor",
                4: "Dining Table", 5: "Living Room", 6: "Bathroom",
                7: "Bedroom"
            }
        
        if not data:
            return {
                'locations_visited': 0,
                'distribution': {},
                'most_visited': 'No data'
            }
        
        areas = []
        for d in data:
            val = d.get('Area', d.get('Lokasi', 0))
            if isinstance(val, str) and not val.isdigit():
                areas.append(val)
            else:
                try:
                    areas.append(AREA_MAP.get(int(val), 'Unknown'))
                except ValueError:
                    areas.append('Unknown')
        
        distribution = Counter(areas)
        
        return {
            'locations_visited': len(distribution),
            'distribution': dict(distribution.most_common()),
            'most_visited': distribution.most_common(1)[0][0] if distribution else 'Unknown'
        }
    
    @staticmethod
    def _analyze_calories(data):
        """Analyze calorie intake vs burned"""
        if not data:
            return {
                'average_intake': 0,
                'average_burned': 0,
                'total_intake': 0,
                'total_burned': 0,
                'net_balance': 0,
                'status': 'No data'
            }
        
        intakes = [int(d.get('Calories', d.get('calories', 0))) for d in data]
        burns = [int(d.get('Calories_burned', d.get('calories_burned', 0))) for d in data]
        
        avg_in = np.mean(intakes) if intakes and any(i > 0 for i in intakes) else 0
        avg_out = np.mean(burns) if burns else 0
        
        net = avg_in - avg_out
        
        if avg_in == 0:
            status = "Monitoring Burned Only (No Intake Logged)"
        elif net < -500:
            status = "Significant Deficit"
        elif net < 0:
            status = "Mild Deficit"
        elif net > 500:
            status = "Significant Surplus"
        else:
            status = "Balanced"
            
        return {
            'average_intake': round(float(avg_in), 1),
            'average_burned': round(float(avg_out), 1),
            'total_intake': int(np.sum(intakes)),
            'total_burned': int(np.sum(burns)),
            'net_balance': round(float(net), 1),
            'status': status
        }
    
    @staticmethod
    def _summarize_alerts(alerts):
        """Summarize alerts"""
        severity_count = Counter([a.get('severity', 'UNKNOWN') for a in alerts])
        
        return {
            'total_alerts': len(alerts),
            'by_severity': dict(severity_count),
            'critical_count': severity_count.get('CRITICAL', 0),
            'warning_count': severity_count.get('WARNING', 0),
            'critical_alerts': [a for a in alerts if a.get('severity') == 'CRITICAL'],
            'warning_alerts': [a for a in alerts if a.get('severity') == 'WARNING']
        }
    
    @staticmethod
    def _summarize_agent_logs(logs):
        """Summarize agent activity"""
        agent_count = Counter([log.get('agent', 'Unknown') for log in logs])
        
        return {
            'total_activities': len(logs),
            'by_agent': dict(agent_count),
            'recent_activities': logs[-20:] if logs else []  # Last 20 activities
        }
    
    @staticmethod
    def _get_risk_level(risk_score):
        """Convert risk score to text level"""
        if risk_score >= 0.7:
            return 'HIGH'
        elif risk_score >= 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    @staticmethod
    def export_to_html(report_data):
        """Convert report to beautiful HTML format"""
        metadata = report_data['metadata']
        vitals = report_data['vital_signs']
        activities = report_data['activity_summary']
        locations = report_data['location_analysis']
        alerts = report_data['alerts_summary']
        risk = report_data['risk_assessment']
        nutrition = report_data.get('nutritional_analysis', {})
        agent_activity = report_data['agent_activity']
        graph_mem = report_data.get('graph_memory_summary', '')
        ai_nar = report_data.get('ai_narrative', '')
        
        # Format timestamps
        try:
            start_time = datetime.fromisoformat(metadata['time_range']['start']).strftime('%Y-%m-%d %H:%M:%S')
            end_time = datetime.fromisoformat(metadata['time_range']['end']).strftime('%Y-%m-%d %H:%M:%S')
            generated_time = datetime.fromisoformat(metadata['report_generated']).strftime('%Y-%m-%d %H:%M:%S')
        except:
            start_time = metadata['time_range']['start']
            end_time = metadata['time_range']['end']
            generated_time = metadata['report_generated']
        
        html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UTLMediCore Health Report - {metadata['device_id']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            background: #0f172a; /* Slate 900 */
            color: #cbd5e1; /* Slate 300 */
            padding: 20px;
        }}
        .container {{ 
            max-width: 1000px; 
            margin: 0 auto; 
            background: #1e293b; /* Slate 800 */
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            overflow: hidden;
            border: 1px solid #334155;
        }}
        .header {{ 
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            color: #f8fafc;
            padding: 40px;
            text-align: center;
            border-bottom: 2px solid #00ffcc;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; color: #00ffcc; }}
        .header .device-id {{ font-size: 1.2em; opacity: 0.9; font-family: monospace; }}
        .content {{ padding: 40px; }}
        
        .metadata {{ 
            background: #0f172a;
            border-left: 4px solid #00ffcc;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 8px;
        }}
        .metadata-item {{ margin: 8px 0; }}
        .metadata-label {{ font-weight: 600; color: #94a3b8; }}
        
        h2 {{ 
            color: #00ffcc;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid #334155;
        }}
        
        .risk-banner {{
            text-align: center;
            padding: 30px;
            border-radius: 12px;
            margin: 20px 0;
            font-size: 2em;
            font-weight: bold;
        }}
        .risk-HIGH {{ background: rgba(220, 38, 38, 0.2); color: #ef4444; border: 2px solid #ef4444; }}
        .risk-MEDIUM {{ background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 2px solid #f59e0b; }}
        .risk-LOW {{ background: rgba(16, 185, 129, 0.2); color: #10b981; border: 2px solid #10b981; }}
        
        .stat-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin: 20px 0; 
        }}
        .stat-card {{ 
            background: #0f172a;
            color: #f8fafc;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #334155;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
        }}
        .stat-label {{ 
            font-size: 0.9em; 
            color: #00ffcc;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .stat-value {{ 
            font-size: 2.5em; 
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-detail {{ 
            font-size: 0.9em; 
            color: #94a3b8;
            margin-top: 10px;
        }}
        
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0;
            background: #0f172a;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #334155;
        }}
        thead {{ background: #00ffcc; color: #0f172a; }}
        th, td {{ 
            text-align: left; 
            padding: 15px;
        }}
        th {{ font-weight: 700; text-transform: uppercase; font-size: 0.9em; letter-spacing: 0.5px; }}
        tbody tr {{ border-bottom: 1px solid #334155; }}
        tbody tr:hover {{ background: #1e293b; }}
        
        .alert-item {{ 
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid;
            background: #0f172a;
        }}
        .alert-CRITICAL {{ border-color: #ef4444; color: #fca5a5; }}
        .alert-WARNING {{ border-color: #f59e0b; color: #fde68a; }}
        .alert-timestamp {{ 
            font-weight: 600;
            margin-bottom: 5px;
        }}
        
        .footer {{ 
            background: #0f172a;
            padding: 30px;
            text-align: center;
            color: #94a3b8;
            font-size: 0.9em;
            border-top: 1px solid #334155;
        }}
        
        .no-data {{ 
            text-align: center;
            padding: 40px;
            color: #64748b;
            font-style: italic;
            background: #0f172a;
            border-radius: 8px;
        }}
        
        @media print {{
            body {{ background: white; color: black; padding: 0; }}
            .container {{ box-shadow: none; border: none; }}
            table, .metadata, .stat-card, .footer {{
                background: white !important;
                color: black !important;
                border: 1px solid #ccc !important;
            }}
            thead {{ background: #eee !important; color: black !important; }}
            h2, .stat-label {{ color: black !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>UTLMediCore Health Report</h1>
            <div class="device-id">Patient Device: {metadata['device_id']}</div>
        </div>
        
        <div class="content">
            <div class="metadata">
                <div class="metadata-item">
                    <span class="metadata-label">Report Period:</span> {start_time} to {end_time}
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Duration:</span> {metadata['time_range']['duration_hours']} hours
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Generated:</span> {generated_time}
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">System:</span> UTLMediCore Agentic AI v{metadata.get('system_version', '1.0')}
                </div>
            </div>
            
            <h2>Risk Assessment</h2>
            <div class="risk-banner risk-{risk['risk_level']}">
                Risk Level: {risk['risk_level']} ({risk['current_risk_score']:.2f})
            </div>
"""
        if ai_nar:
            try:
                import markdown
                # Convert markdown narrative to HTML with extensions
                nar_html = markdown.markdown(
                    ai_nar,
                    extensions=['extra', 'nl2br', 'sane_lists']
                )
                html += f"""
            <h2>Expert AI Analysis</h2>
            <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 20px; border-radius: 8px; margin-bottom: 30px; line-height: 1.8; color: #f8fafc;">
                {nar_html}
            </div>
"""
            except:
                # Fallback: render with real newlines as <br>
                formatted_nar = "<br>".join(ai_nar.split("\n"))
                html += f"""
            <h2>Expert AI Analysis</h2>
            <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 20px; border-radius: 8px; margin-bottom: 30px; line-height: 1.8; color: #f8fafc;">
                {formatted_nar}
            </div>
"""

        if graph_mem:
            # Format graph mem text as HTML paragraphs
            formatted_mem = "<br>".join(graph_mem.split("\\n"))
            html += f"""
            <h2>Semantic Memory Records (Graphiti)</h2>
            <div style="background: rgba(139, 92, 246, 0.1); border-left: 4px solid #8b5cf6; padding: 20px; border-radius: 8px; margin-bottom: 30px; line-height: 1.6; color: #f8fafc;">
                {formatted_mem}
            </div>
"""

        # Manual Patient Logs (Meals, Activities, Medical Records)
        manual_ctx = report_data.get('manual_context', [])
        if manual_ctx:
            html += """
            <h2>Manual Patient Logs (Self-Reported Data)</h2>
            <div style="background: rgba(0, 255, 204, 0.06); border: 1px solid rgba(0, 255, 204, 0.25); border-radius: 12px; padding: 20px; margin-bottom: 30px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                    <span style="background: #00ffcc; color: #0f172a; padding: 4px 12px; border-radius: 6px; font-weight: 700; font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px;">Data Source</span>
                    <span style="color: #94a3b8; font-size: 0.9em;">These logs were manually entered by the patient or caregiver and were <strong style="color: #00ffcc;">used as input data</strong> for the AI Expert Analysis and Recommendations above.</span>
                </div>
                <table style="margin: 0;">
                    <thead>
                        <tr>
                            <th style="width: 160px;">Timestamp (UTC+8)</th>
                            <th style="width: 120px;">Category</th>
                            <th>Patient Description</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for entry in manual_ctx:
                from utils.tz_utils import utc_to_utc8
                ts = utc_to_utc8(entry.get('timestamp', ''))
                cat_raw = entry.get('name', 'unknown')
                if cat_raw.startswith('meal'):
                    cat_label = 'Meal'
                    badge_color = '#00ffcc'
                elif cat_raw.startswith('activity'):
                    cat_label = 'Activity'
                    badge_color = '#facc15'
                elif cat_raw.startswith('medical'):
                    cat_label = 'Medical Record'
                    badge_color = '#a066ff'
                else:
                    cat_label = cat_raw
                    badge_color = '#94a3b8'
                content = entry.get('content', '')
                html += f"""
                        <tr>
                            <td style="font-family: monospace; font-size: 0.85em; white-space: nowrap;">{ts}</td>
                            <td><span style="background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}44; padding: 3px 10px; border-radius: 4px; font-size: 0.8em; font-weight: 600;">{cat_label}</span></td>
                            <td>{content}</td>
                        </tr>
"""
            html += """
                    </tbody>
                </table>
            </div>
"""
        else:
            html += """
            <h2>Manual Patient Logs (Self-Reported Data)</h2>
            <div class="no-data">No manual logs were recorded by the patient or caregiver during this period. Encourage the patient to log meals, activities, and medical events for more accurate AI recommendations.</div>
"""

        # Vital Signs
        html += """
            <h2>Vital Signs Summary</h2>
"""
        
        if vitals.get('heart_rate', {}).get('readings_count', 0) > 0:
            hr = vitals['heart_rate']
            spo2 = vitals['blood_oxygen']
            
            html += f"""
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Heart Rate</div>
                    <div class="stat-value">{hr['average']} <small style="font-size:0.5em">bpm</small></div>
                    <div class="stat-detail">
                        📊 Range: {hr['minimum']} - {hr['maximum']} bpm<br>
                        📈 Std Dev: ±{hr['std_deviation']} bpm<br>
                        ⚠️ Abnormal: {hr['abnormal_readings']} readings
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Blood Oxygen</div>
                    <div class="stat-value">{spo2['average']} <small style="font-size:0.5em">%</small></div>
                    <div class="stat-detail">
                        📊 Range: {spo2['minimum']} - {spo2['maximum']}%<br>
                        🫁 Hypoxia Events: {spo2['hypoxia_events']}<br>
                        📍 Total Readings: {spo2['readings_count']}
                    </div>
                </div>
            </div>
"""
        else:
            html += '<div class="no-data">❌ No vital signs data available in this time range</div>'
        
        # Nutrition Summary
        html += """
            <h2>Nutritional Analysis</h2>
"""
        if nutrition.get('status') != 'No data':
            html += f"""
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Avg. Calorie Intake</div>
                    <div class="stat-value">{nutrition['average_intake']} <small style="font-size:0.5em">Kcal</small></div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg. Calorie Burned</div>
                    <div class="stat-value">{nutrition['average_burned']} <small style="font-size:0.5em">Kcal</small></div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Net Balance</div>
                    <div class="stat-value">{nutrition['net_balance']} <small style="font-size:0.5em">Kcal</small></div>
                    <div class="stat-detail">Status: <strong>{nutrition['status']}</strong></div>
                </div>
            </div>
"""
        else:
            html += '<div class="no-data">No nutritional data available</div>'
        
        # Activity Summary
        html += """
            <h2>Activity Summary</h2>
"""
        
        if activities.get('total_readings', 0) > 0:
            html += f"""
            <p><strong>Most Common Activity:</strong> {activities['most_common_activity']}</p>
            <p><strong>Total Readings:</strong> {activities['total_readings']}</p>
            <table>
                <thead>
                    <tr>
                        <th>Activity/Posture</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            for activity, stats in list(activities['distribution'].items())[:10]:
                html += f"""
                    <tr>
                        <td>{activity}</td>
                        <td>{stats['count']}</td>
                        <td>{stats['percentage']}%</td>
                    </tr>
"""
            
            html += """
                </tbody>
            </table>
"""
        else:
            html += '<div class="no-data">No activity data available</div>'
        
        # Location Analysis
        html += """
            <h2>Location Analysis</h2>
"""
        
        if locations.get('locations_visited', 0) > 0:
            html += f"""
            <p><strong>Most Visited Location:</strong> {locations['most_visited']}</p>
            <p><strong>Unique Locations:</strong> {locations['locations_visited']}</p>
            <table>
                <thead>
                    <tr>
                        <th>Location</th>
                        <th>Visit Count</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            for location, count in list(locations['distribution'].items())[:10]:
                html += f"""
                    <tr>
                        <td>{location}</td>
                        <td>{count}</td>
                    </tr>
"""
            
            html += """
                </tbody>
            </table>
"""
        else:
            html += '<div class="no-data">No location data available</div>'
        
        # Alerts Summary
        html += f"""
            <h2>Alerts Summary</h2>
            <p><strong>Total Alerts:</strong> {alerts['total_alerts']}</p>
"""
        
        if alerts.get('by_severity'):
            html += '<p><strong>By Severity:</strong> '
            html += ', '.join([f"{sev}: {count}" for sev, count in alerts['by_severity'].items()])
            html += '</p>'
        
        if alerts.get('critical_alerts'):
            html += '<h3 style="color: #dc2626; margin-top: 20px;">Critical Alerts</h3>'
            for alert in alerts['critical_alerts'][:10]:
                timestamp = alert.get('timestamp', 'N/A')
                message = alert.get('message', 'No message')
                html += f'''
                <div class="alert-item alert-CRITICAL">
                    <div class="alert-timestamp">⏰ {timestamp}</div>
                    <div>{message}</div>
                </div>
'''
        
        if alerts.get('warning_alerts'):
            html += '<h3 style="color: #f59e0b; margin-top: 20px;">Warning Alerts</h3>'
            for alert in alerts['warning_alerts'][:10]:
                timestamp = alert.get('timestamp', 'N/A')
                message = alert.get('message', 'No message')
                html += f'''
                <div class="alert-item alert-WARNING">
                    <div class="alert-timestamp">⏰ {timestamp}</div>
                    <div>{message}</div>
                </div>
'''
        
        if alerts['total_alerts'] == 0:
            html += '<div class="no-data">✅ No alerts in this time period</div>'
        
        # Agent Activity
        html += f"""
            <h2>Agent Activity Summary</h2>
            <p><strong>Total Agent Activities:</strong> {agent_activity['total_activities']}</p>
"""
        
        if agent_activity.get('by_agent'):
            html += """
            <table>
                <thead>
                    <tr>
                        <th>Agent</th>
                        <th>Activity Count</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            for agent, count in agent_activity['by_agent'].items():
                html += f"""
                    <tr>
                        <td>{agent}</td>
                        <td>{count}</td>
                    </tr>
"""
            
            html += """
                </tbody>
            </table>
"""
        
        # Footer
        html += """
        </div>
        
        <div class="footer">
            <p><strong>🏥 UTLMediCore Agentic AI System</strong></p>
            <p>This report is generated by autonomous AI agents for informational purposes.</p>
            <p>All findings should be reviewed by qualified medical personnel.</p>
            <p style="margin-top: 15px; font-size: 0.85em;">© 2026 UTLMediCore | Advanced Health Monitoring</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
