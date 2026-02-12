"""
Health Report Generator for UTLMediCore
Generate comprehensive patient health reports in JSON and HTML formats
"""

from datetime import datetime, timedelta
import json
from collections import Counter
import numpy as np


class ReportGenerator:
    """Generate comprehensive health reports for patients"""
    
    @staticmethod
    def generate_report(patient_state, alerts, agent_logs, time_range_hours=24):
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
        
        # Generate report sections
        report = {
            'metadata': ReportGenerator._generate_metadata(
                patient_state.device_id, 
                time_range_hours
            ),
            'vital_signs': ReportGenerator._analyze_vitals(recent_data),
            'activity_summary': ReportGenerator._analyze_activities(recent_data),
            'location_analysis': ReportGenerator._analyze_locations(recent_data),
            'alerts_summary': ReportGenerator._summarize_alerts(recent_alerts),
            'agent_activity': ReportGenerator._summarize_agent_logs(recent_logs),
            'risk_assessment': {
                'current_risk_score': patient_state.risk_score,
                'risk_level': ReportGenerator._get_risk_level(patient_state.risk_score)
            },
            'raw_data_sample': recent_data[:50] if recent_data else []  # Last 50 readings for reference
        }
        
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
        
        postures = [
            POSTURE_MAP.get(int(d.get('Posture_state', 0)), 'Unknown') 
            for d in data
        ]
        
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
        
        areas = [
            AREA_MAP.get(int(d.get('Area', d.get('Lokasi', 0))), 'Unknown')
            for d in data
        ]
        
        distribution = Counter(areas)
        
        return {
            'locations_visited': len(distribution),
            'distribution': dict(distribution.most_common()),
            'most_visited': distribution.most_common(1)[0][0] if distribution else 'Unknown'
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
        agent_activity = report_data['agent_activity']
        
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
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{ 
            max-width: 1000px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header .device-id {{ font-size: 1.2em; opacity: 0.9; }}
        .content {{ padding: 40px; }}
        
        .metadata {{ 
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 8px;
        }}
        .metadata-item {{ margin: 8px 0; }}
        .metadata-label {{ font-weight: 600; color: #495057; }}
        
        h2 {{ 
            color: #667eea;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .risk-banner {{
            text-align: center;
            padding: 30px;
            border-radius: 12px;
            margin: 20px 0;
            font-size: 2em;
            font-weight: bold;
        }}
        .risk-HIGH {{ background: #fee2e2; color: #dc2626; border: 3px solid #dc2626; }}
        .risk-MEDIUM {{ background: #fef3c7; color: #f59e0b; border: 3px solid #f59e0b; }}
        .risk-LOW {{ background: #d1fae5; color: #16a34a; border: 3px solid #16a34a; }}
        
        .stat-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin: 20px 0; 
        }}
        .stat-card {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
        .stat-label {{ 
            font-size: 0.9em; 
            opacity: 0.9;
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
            opacity: 0.85;
            margin-top: 10px;
        }}
        
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        thead {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        th, td {{ 
            text-align: left; 
            padding: 15px;
        }}
        th {{ font-weight: 600; text-transform: uppercase; font-size: 0.9em; letter-spacing: 0.5px; }}
        tbody tr {{ border-bottom: 1px solid #e9ecef; }}
        tbody tr:hover {{ background: #f8f9fa; }}
        
        .alert-item {{ 
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid;
        }}
        .alert-CRITICAL {{ 
            background: #fee2e2; 
            border-color: #dc2626;
        }}
        .alert-WARNING {{ 
            background: #fef3c7; 
            border-color: #f59e0b;
        }}
        .alert-timestamp {{ 
            font-weight: 600;
            margin-bottom: 5px;
        }}
        
        .footer {{ 
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            border-top: 1px solid #e9ecef;
        }}
        
        .no-data {{ 
            text-align: center;
            padding: 40px;
            color: #6c757d;
            font-style: italic;
        }}
        
        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> UTLMediCore Health Report</h1>
            <div class="device-id">Patient Device: {metadata['device_id']}</div>
        </div>
        
        <div class="content">
            <div class="metadata">
                <div class="metadata-item">
                    <span class="metadata-label">📅 Report Period:</span> {start_time} to {end_time}
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">⏱️ Duration:</span> {metadata['time_range']['duration_hours']} hours
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">🕐 Generated:</span> {generated_time}
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">🤖 System:</span> UTLMediCore Agentic AI v{metadata.get('system_version', '1.0')}
                </div>
            </div>
            
            <h2> Risk Assessment</h2>
            <div class="risk-banner risk-{risk['risk_level']}">
                Risk Level: {risk['risk_level']} ({risk['current_risk_score']:.2f})
            </div>
"""
        
        # Vital Signs
        html += """
            <h2> Vital Signs Summary</h2>
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
        
        # Activity Summary
        html += """
            <h2> Activity Summary</h2>
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
            html += '<div class="no-data">❌ No activity data available</div>'
        
        # Location Analysis
        html += """
            <h2>📍 Location Analysis</h2>
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
            html += '<div class="no-data">❌ No location data available</div>'
        
        # Alerts Summary
        html += f"""
            <h2>🚨 Alerts Summary</h2>
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
            <h2> Agent Activity Summary</h2>
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
