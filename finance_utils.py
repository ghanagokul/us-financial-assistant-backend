import yfinance as yf
import datetime

def get_etf_summary(ticker):
    try:
        etf = yf.Ticker(ticker)
        info = etf.info

        # Get price
        price = round(info.get("regularMarketPrice", 0), 2)

        # Get dividend yield safely
        raw_yield = info.get("dividendYield")
        yield_percent = round(raw_yield * 100, 2) if isinstance(raw_yield, (int, float)) else "N/A"

        # Get expense ratio
        expense_ratio = round(info.get("expenseRatio", 0) * 100, 2) if isinstance(info.get("expenseRatio"), (int, float)) else "N/A"

        # Calculate 3Y return using historical prices
        cagr = calculate_3y_cagr(etf)

        return {
            "symbol": ticker,
            "name": info.get("shortName", ticker),
            "price": price,
            "yield": yield_percent,
            "expenseRatio": expense_ratio,
            "3yReturn": cagr,
            "category": info.get("category", "N/A")
        }

    except Exception as e:
        print(f"⚠️ Error fetching data for {ticker}: {e}")
        return {
            "symbol": ticker,
            "name": ticker,
            "price": 0,
            "yield": "N/A",
            "expenseRatio": "N/A",
            "3yReturn": "N/A",
            "category": "N/A"
        }

def calculate_3y_cagr(etf):
    try:
        end = datetime.datetime.today()
        start = end - datetime.timedelta(days=3 * 365)
        hist = etf.history(start=start, end=end)

        if hist.empty or "Close" not in hist.columns:
            return "N/A"

        start_price = hist["Close"].iloc[0]
        end_price = hist["Close"].iloc[-1]

        if start_price == 0:
            return "N/A"

        cagr = ((end_price / start_price) ** (1 / 3)) - 1
        return f"{round(cagr * 100, 2)}%"

    except Exception as e:
        print(f"⚠️ Error calculating CAGR: {e}")
        return "N/A"
