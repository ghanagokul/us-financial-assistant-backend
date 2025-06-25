# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class InvestmentQuery(db.Model):
    __tablename__ = 'investment_queries'

    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=True)
    income = db.Column(db.Float, nullable=True)
    monthly_sip = db.Column(db.Float, nullable=True)
    visa_status = db.Column(db.String(100), default='Not specified')
    remittance = db.Column(db.Boolean, default=False)
    risk = db.Column(db.String(50), default='Medium')
    goal = db.Column(db.String(100), default='Wealth Growth')
    duration = db.Column(db.String(100), default='Medium Term (3–10 years)')
    sectors = db.Column(db.Text, nullable=True)  # comma-separated list or JSON
    query = db.Column(db.Text, nullable=True)
    response = db.Column(db.Text, nullable=True)  # GPT output
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
