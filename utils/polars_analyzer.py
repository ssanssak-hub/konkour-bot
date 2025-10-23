# utils/polars_analyzer.py
import polars as pl
from datetime import datetime
from typing import List, Dict, Any

class StudyAnalyzer:
    """تحلیل‌گر داده‌های مطالعه با Polars"""
    
    def __init__(self):
        self.df = None
    
    def load_data(self, sessions: List[Dict]):
        """بارگذاری داده‌ها در Polars DataFrame"""
        self.df = pl.DataFrame(sessions)
        
        # تبدیل تاریخ اگر وجود دارد
        if 'date' in self.df.columns:
            self.df = self.df.with_columns(
                pl.col('date').str.strptime(pl.Date, '%Y-%m-%d')
            )
    
    def get_study_stats(self) -> Dict[str, Any]:
        """آمار کلی مطالعه"""
        if self.df is None or self.df.is_empty():
            return {"error": "No data available"}
        
        stats = self.df.select([
            pl.sum('study_hours').alias('total_hours'),
            pl.len().alias('total_sessions'),
            pl.mean('study_hours').alias('avg_hours'),
            pl.max('study_hours').alias('max_hours'),
            pl.min('study_hours').alias('min_hours')
        ])
        
        return stats.row(0)
    
    def get_subject_analysis(self) -> List[Dict]:
        """تحلیل عملکرد دروس"""
        if self.df is None or self.df.is_empty():
            return []
        
        subject_stats = self.df.group_by('subject').agg([
            pl.sum('study_hours').alias('total_hours'),
            pl.mean('study_hours').alias('avg_hours'),
            pl.len().alias('session_count')
        ]).sort('total_hours', descending=True)
        
        return subject_stats.to_dicts()
    
    def generate_report(self, user_id: int) -> str:
        """تولید گزارش برای کاربر"""
        stats = self.get_study_stats()
        subjects = self.get_subject_analysis()
        
        report = [
            "📊 **گزارش تحلیلی مطالعه**",
            f"⏱️ مجموع ساعت مطالعه: {stats['total_hours']:.1f} ساعت",
            f"📚 تعداد جلسات: {stats['total_sessions']}",
            f"📈 میانگین ساعت مطالعه: {stats['avg_hours']:.1f} ساعت",
            "",
            "🎯 **برترین دروس:**"
        ]
        
        for i, subject in enumerate(subjects[:3], 1):
            report.append(
                f"{i}. {subject['subject']}: {subject['total_hours']:.1f} ساعت"
            )
        
        return "\n".join(report)

# استفاده در ربات
analyzer = StudyAnalyzer()
