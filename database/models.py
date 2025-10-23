from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(100), index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    phone_number = Column(String(15))
    join_date = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    language = Column(String(10), default='fa')
    timezone = Column(String(50), default='Asia/Tehran')
    settings = Column(JSON, default=lambda: {})
    
    # روابط
    attendance_records = relationship("Attendance", back_populates="user", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("UserMessage", back_populates="user", cascade="all, delete-orphan")
    timers = relationship("StudyTimer", back_populates="user", cascade="all, delete-orphan")
    exam_preferences = relationship("UserExamPreference", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, user_id={self.user_id}, username='{self.username}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'is_active': self.is_active,
            'is_premium': self.is_premium,
            'language': self.language,
            'settings': self.settings
        }

class Attendance(Base):
    __tablename__ = 'attendance'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    date = Column(String(10), nullable=False, index=True)
    check_in_time = Column(String(8))
    check_out_time = Column(String(8))
    duration_minutes = Column(Integer, default=0)
    notes = Column(Text)
    
    user = relationship("User", back_populates="attendance_records")
    
    def __repr__(self):
        return f"<Attendance(user_id={self.user_id}, date='{self.date}')>"

class StudyPlan(Base):
    __tablename__ = 'study_plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=False)
    plan_type = Column(String(20), nullable=False)
    target_hours = Column(Float, nullable=False)
    completed_hours = Column(Float, default=0)
    deadline = Column(String(10))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_completed = Column(Boolean, default=False)
    priority = Column(Integer, default=1)
    color = Column(String(7), default='#3498db')
    tags = Column(JSON, default=lambda: [])
    
    user = relationship("User", back_populates="study_plans")
    
    def __repr__(self):
        return f"<StudyPlan(user_id={self.user_id}, title='{self.title}', type='{self.plan_type}')>"
    
    def progress_percentage(self):
        if self.target_hours == 0:
            return 0
        return min((self.completed_hours / self.target_hours) * 100, 100)

class StudySession(Base):
    __tablename__ = 'study_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    subject = Column(String(100), nullable=False)
    duration = Column(Float, nullable=False)
    date = Column(String(10), nullable=False, index=True)
    start_time = Column(String(8))
    end_time = Column(String(8))
    notes = Column(Text)
    mood = Column(Integer)
    productivity = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="study_sessions")
    
    def __repr__(self):
        return f"<StudySession(user_id={self.user_id}, subject='{self.subject}', duration={self.duration})>"

class Reminder(Base):
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    reminder_type = Column(String(50), nullable=False)
    title = Column(String(200))
    exam_name = Column(String(100))
    custom_message = Column(Text)
    reminder_time = Column(String(5), nullable=False)
    days_of_week = Column(JSON, default=lambda: [])
    is_active = Column(Boolean, default=True)
    is_recurring = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_triggered = Column(DateTime)
    
    user = relationship("User", back_populates="reminders")
    
    def __repr__(self):
        return f"<Reminder(user_id={self.user_id}, type='{self.reminder_type}', time='{self.reminder_time}')>"

class UserMessage(Base):
    __tablename__ = 'user_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    admin_id = Column(Integer)
    message_text = Column(Text, nullable=False)
    message_type = Column(String(20), default='general')
    status = Column(String(20), default='pending')
    admin_reply = Column(Text)
    reply_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = relationship("User", back_populates="messages")
    
    def __repr__(self):
        return f"<UserMessage(user_id={self.user_id}, status='{self.status}')>"

class StudyTimer(Base):
    __tablename__ = 'study_timers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(100))
    target_hours = Column(Float, nullable=False)
    remaining_hours = Column(Float, nullable=False)
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_paused = Column(Boolean, default=False)
    paused_duration = Column(Float, default=0)
    completed_sessions = Column(Integer, default=0)
    
    user = relationship("User", back_populates="timers")
    
    def __repr__(self):
        return f"<StudyTimer(user_id={self.user_id}, title='{self.title}', remaining={self.remaining_hours})>"

class UserExamPreference(Base):
    __tablename__ = 'user_exam_preferences'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    exam_name = Column(String(100), nullable=False)
    is_selected = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    target_score = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="exam_preferences")
    
    def __repr__(self):
        return f"<UserExamPreference(user_id={self.user_id}, exam='{self.exam_name}')>"

class SystemLog(Base):
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False)
    module = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    user_id = Column(Integer)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<SystemLog(level='{self.level}', module='{self.module}')>"
