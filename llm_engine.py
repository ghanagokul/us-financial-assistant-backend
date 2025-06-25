import os
from dotenv import load_dotenv
from openai import OpenAI
from finance_utils import get_etf_summary  # Import ETF data function

# Load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------- Function 1: Generate Personalized Investment Plan -------------------
def get_advice(data):
    if "monthly_sip" in data and data["monthly_sip"]:
        monthly_sip = data["monthly_sip"]
    else:
        monthly_income = data["income"] / 12
        monthly_sip = round(monthly_income * 0.15, 2)

    # Define ETF categories
    stock_etfs = [
        ("VTI", get_etf_summary("VTI")),
        ("SCHD", get_etf_summary("SCHD")),
        ("SPY", get_etf_summary("SPY")),
        ("QQQ", get_etf_summary("QQQ")),
        ("VUG", get_etf_summary("VUG")),
        ("VTV", get_etf_summary("VTV"))
    ]
    bond_etfs = [
        ("BND", get_etf_summary("BND")),
        ("IEF", get_etf_summary("IEF")),
        ("TLT", get_etf_summary("TLT")),
        ("AGG", get_etf_summary("AGG"))
    ]
    sector_etfs = {
        "Technology": (get_etf_summary("XLK"), "High"),
        "Healthcare": (get_etf_summary("XLV"), "Low"),
        "Energy": (get_etf_summary("XLE"), "Medium"),
        "Financials": (get_etf_summary("XLF"), "Medium"),
        "Industrials": (get_etf_summary("XLI"), "Medium"),
        "Materials": (get_etf_summary("XLB"), "Medium"),
        "Consumer Discretionary": (get_etf_summary("XLY"), "High"),
        "Consumer Staples": (get_etf_summary("XLP"), "Low"),
        "Communication Services": (get_etf_summary("XLC"), "High"),
        "Global Real Estate": (get_etf_summary("REET"), "Medium"),
        "Real Estate": (get_etf_summary("XLRE"), "Medium")
    }

    preferred_sector_notes = ""
    if data.get("sectors"):
        preferred_sector_notes = "\n\n**Preferred Sector Insights:**"
        for sector in data["sectors"]:
            sector_clean = sector.strip()
            if sector_clean in sector_etfs:
                etf, risk = sector_etfs[sector_clean]
                preferred_sector_notes += (
                    f"\n- {sector_clean} (ETF: {etf['symbol']}): Price ${etf['price']}, "
                    f"Yield {etf['yield']}, 3Y Return {etf['3yReturn']} | Risk Level: {risk}"
                )

    used_etfs = {symbol for sector, (etf, _) in sector_etfs.items() for symbol in [etf['symbol']]}

    etf_notes = f"""
## 📈 Live ETF Data Snapshot

Provide insights based on the following ETF data:

- Stock ETFs:
{chr(10).join([f"  - {symbol}: ${info['price']} | Yield: {info['yield']} | 3Y Return: {info['3yReturn']}" for symbol, info in stock_etfs if symbol in used_etfs])}

- Bond ETFs:
{chr(10).join([f"  - {symbol}: ${info['price']} | Yield: {info['yield']} | 3Y Return: {info['3yReturn']}" for symbol, info in bond_etfs if symbol in used_etfs])}

- Sector ETFs:
{chr(10).join([f"  - {sector}: ${info[0]['price']} | Yield: {info[0]['yield']} | 3Y Return: {info[0]['3yReturn']} | Risk: {info[1]}" for sector, info in sector_etfs.items() if info[0]['symbol'] in used_etfs])}
{preferred_sector_notes}
"""

    # 🧠 Prompt with Chain-of-Thought and Role-based prompting
    prompt = f"""
You are a **professional financial advisor** who specializes in assisting **migrants living in the U.S.** with building safe, long-term **Automatic Investment Plans (AIPs)** tailored to their financial goals, visa considerations, and life circumstances.

🔄 Think step by step before writing the final plan:
- First, **reflect deeply** on the user's background, income, visa status, goals, risk tolerance, and duration.
- Next, evaluate **optimal ETF combinations** based on risk-return profiles, sector strengths, and economic forecasts.
- Finally, build a friendly and insightful strategy tailored for someone adapting to U.S. financial systems.

Generate a clear, well-structured response using the format below:

## 🧠 Personalized Investment Strategy (U.S. Migrant Focused)

1. 👤 **User Overview**  
   Brief summary based on visa status, income, goal, and investment duration.

2. 📈 **Portfolio Allocation Plan**  
   - Choose Stock, Bond, and Sector ETFs from the user's preferred lists or general high-performance options.
   - Justify each ETF based on yield, return history, volatility, and relevance to goals.
   - Assign percentage allocations that balance risk and growth potential.

3. 🏢 **Best Sectors to Focus On**  
   Recommend 2–3 sectors that align with the user's goals and reflect current U.S. economic trends.

4. 🔎 **Why This Strategy Fits**  
   Explain why this strategy suits the user, considering their:
   - Visa limitations
   - Remittance needs
   - Risk tolerance
   - Time horizon and job flexibility

5. 📈 **Return Projections (Min–Max in 3 Years)**  
   Simulate expected portfolio growth using conservative (5%) and optimistic (8%) annual return scenarios.

6. 💬 **Advisor Notes & Migrant-Specific Tips**  
   - Suggestions for building an emergency fund
   - Preparing for possible visa/job transitions
   - Tax-saving opportunities (e.g., Roth IRA, 401(k), tax-loss harvesting)
   - Resources for migrant financial literacy

7. 💰 **Recommended Monthly SIP Amount**  
   Based on the user's income, propose a realistic and flexible monthly investment amount.
   Justify your suggestion using a percentage-based reasoning (e.g., 10–20% of monthly income).

8. 📈 **Live ETF Data Snapshot**  
   Include only the ETF notes that are part of the recommended portfolio allocation.
   {etf_notes}

### 👤 User Profile:
- Age: {data['age']}
- Annual Income: ${data.get('income', 'Not provided')}
- Risk Tolerance: {data['risk']}
- Investment Goal: {data['goal']}
- Investment Duration: {data['duration']}
- Visa Status: {data['visa_status']}
- Sends Money Back Home: {'Yes' if data['remittance'] else 'No'}
- Preferred Sectors: {", ".join(data.get('sectors', [])) if data.get('sectors') else 'No preference'}
- Monthly Investment Amount: ${monthly_sip}
- User's Query: {data['query']}
"""

    try:
        response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful financial advisor who is expert and creates expert version of investment plans for migrants in the U.S."
        },
        {"role": "user", "content": prompt}
    ],
    temperature=0.4,
    top_p=0.9,         # nucleus sampling: consider top 90% of tokens by probability
    max_tokens=1300
)

        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"

# ------------------- Function 2: Explain Financial Terms Concisely -------------------
def explain_concept(concept):
    prompt = f"""
Explain the following financial concept in a short, beginner-friendly way. 
- Keep it clear and under 3 bullet points or 3 sentences.
- Use simple words.

Concept: {concept}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a finance tutor. Keep your explanations short, clear, and simple unless the user asks for more detail."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error explaining concept: {str(e)}"
