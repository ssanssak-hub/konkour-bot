# utils/modern_analyzer.py
"""
سیستم تحلیل داده‌های مدرن با Polars (جایگزین pandas)
"""
try:
    import polars as pl
    PANDAS_AVAILABLE = False
except ImportError:
    PANDAS_AVAILABLE = False

import json
from datetime import datetime
from typing import List, Dict, Any

class ModernAnalyzer:
    """تحلیل‌گر داده‌های مدرن برای پایتون 3.14"""
    
    def __init__(self):
        self.use_polars = PANDAS_AVAILABLE
    
    def analyze_study_data(self, sessions: List[Dict]) -> Dict[str, Any]:
        """تحلیل داده‌های مطالعه"""
        if not sessions:
            return {"error": "No data available"}
        
        if self.use_polars:
            return self._analyze_with_polars(sessions)
        else:
            return self._analyze_manual(sessions)
    
    def _analyze_with_polars(self, sessions: List[Dict]) -> Dict[str, Any]:
        """تحلیل با Polars"""
        df = pl.DataFrame(sessions)
        
        stats = df.select([
            pl.sum("study_hours").alias("total_hours"),
            pl.count().alias("total_sessions"),
            pl.mean("study_hours").alias("avg_hours")
        ])
        
        subject_stats = df.group_by("subject").agg([
            pl.sum("study_hours").alias("total_hours"),
            pl.count().alias("sessions")
        ])
        
        return {
            "total_hours": stats["total_hours"][0],
            "total_sessions": stats["total_sessions"][0],
            "avg_hours": stats["avg_hours"][0],
            "subjects": subject_stats.to_dicts()
        }
    
    def _analyze_manual(self, sessions: List[Dict]) -> Dict[str, Any]:
        """تحلیل دستی"""
        total_hours = sum(s.get('study_hours', 0) for s in sessions)
        total_sessions = len(sessions)
        avg_hours = total_hours / total_sessions if total_sessions > 0 else 0
        
        subjects = {}
        for session in sessions:
            subject = session.get('subject')
            if subject:
                subjects[subject] = subjects.get(subject, 0) + session.get('study_hours', 0)
        
        return {
            "total_hours": total_hours,
            "total_sessions": total_sessions,
            "avg_hours": round(avg_hours, 2),
            "subjects": subjects
        }

# استفاده در ربات
analyzer = ModernAnalyzer()
