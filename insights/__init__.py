"""
Insights module for UTLMediCore
Report generation with graceful fallbacks.
"""

# Graceful import - crewai may not work on Python 3.14
try:
    from insights.crewai_aisuite_adapter import get_aisuite_llm, AISuiteLLM
    from insights.report_crew import get_report_crew, ReportNarrativeCrew
    CREWAI_AVAILABLE = True
except Exception:
    CREWAI_AVAILABLE = False
    get_aisuite_llm = None
    AISuiteLLM = None
    get_report_crew = None
    ReportNarrativeCrew = None

# Always available - no heavy dependencies
from insights.lite_report_agent import generate_lite_narrative

__all__ = [
    'get_aisuite_llm',
    'AISuiteLLM',
    'get_report_crew',
    'ReportNarrativeCrew',
    'generate_lite_narrative',
    'CREWAI_AVAILABLE',
]
