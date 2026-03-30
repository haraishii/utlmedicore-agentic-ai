"""
Timezone utility for converting Neo4j UTC timestamps to UTC+8.
Handles nanosecond precision timestamps from Neo4j.
"""

from datetime import datetime, timedelta
import re

def utc_to_utc8(ts_raw: str) -> str:
    """
    Convert a UTC timestamp string to UTC+8 formatted string.
    Handles Neo4j nanosecond precision: '2026-03-26T04:23:00.000000000+00:00'
    Returns: '2026-03-26 12:23' (UTC+8)
    """
    if not ts_raw:
        return ''
    try:
        # Strip timezone suffix (+00:00 or Z)
        clean = re.sub(r'[+].*$', '', ts_raw)
        clean = clean.rstrip('Z')
        
        # Truncate nanoseconds to microseconds (Python supports max 6 digits)
        # Match pattern: .123456789 -> .123456
        clean = re.sub(r'\.(\d{6})\d+', r'.\1', clean)
        
        dt = datetime.fromisoformat(clean)
        dt_local = dt + timedelta(hours=8)
        return dt_local.strftime('%Y-%m-%d %H:%M')
    except Exception:
        # Fallback: just take first 16 chars and replace T with space
        return ts_raw[:16].replace('T', ' ')
