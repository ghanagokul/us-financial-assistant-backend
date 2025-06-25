from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import desc
from llm_engine import get_advice
from models import db, InvestmentQuery
import os

app = Flask(__name__)
CORS(app)

# PostgreSQL config (safe fallback for first deploy)
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("⚠️ DATABASE_URL not found — skipping DB init for now.")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

@app.route('/invest', methods=['POST'])
def invest():
    data = request.json
    print("✅ Received request:", data)

    try:
        # Clean and standardize input
        income = float(data.get('income')) if data.get('income') else None
        monthly_sip = float(data.get('monthly_sip')) if data.get('monthly_sip') else None
        age = int(data.get('age')) if data.get('age') else None
        visa_status = data.get('visa_status', 'Not specified')
        remittance = bool(data.get('remittance', False))
        risk = data.get('risk', 'Medium')
        goal = data.get('goal', 'Wealth Growth')
        duration = data.get('duration', 'Medium Term (3–10 years)')
        sectors = data.get('sectors', [])
        user_query = data.get('query', '')

        # Get LLM response
        response = get_advice({
            "income": income,
            "monthly_sip": monthly_sip,
            "age": age,
            "visa_status": visa_status,
            "remittance": remittance,
            "risk": risk,
            "goal": goal,
            "duration": duration,
            "sectors": sectors,
            "query": user_query
        })
        print("✅ Response preview:", response[:300])

        # Store in DB
        new_entry = InvestmentQuery(
            age=age,
            income=income,
            monthly_sip=monthly_sip,
            visa_status=visa_status,
            remittance=remittance,
            risk=risk,
            goal=goal,
            duration=duration,
            sectors=','.join(sectors),
            query=user_query,
            response=response
        )
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({'response': response})

    except Exception as e:
        error_message = f"❌ Error generating advice: {str(e)}"
        print(error_message)
        return jsonify({'error': error_message}), 500

@app.route('/history', methods=['GET'])
def history():
    try:
        recent = db.session.query(InvestmentQuery).order_by(desc(InvestmentQuery.timestamp)).limit(10).all()
        return jsonify([
            {
                'age': entry.age,
                'income': entry.income,
                'sip': entry.monthly_sip,
                'goal': entry.goal,
                'risk': entry.risk,
                'query': entry.query,
                'response': entry.response[:200] if entry.response else '',
                'timestamp': entry.timestamp.isoformat() if entry.timestamp else 'Missing'
            } for entry in recent
        ])
    except Exception as e:
        print("❌ Error in /history route:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
