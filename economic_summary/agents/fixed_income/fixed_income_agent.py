import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

class FixedIncomeAgent:
    def __init__(self):
        # Real Treasury Yield Tickers from Yahoo Finance
        self.tickers = {
            "13W": "^IRX",  # 13-week T-Bill yield
            "5Y": "^FVX",   # 5-year yield
            "10Y": "^TNX",  # 10-year yield
            "30Y": "^TYX"   # 30-year yield
        }
        self.history_days = 30  # How many days of history to fetch

    def fetch_data(self):
        # Download yield data
        end = datetime.today()
        start = end - timedelta(days=self.history_days)
        df = yf.download(list(self.tickers.values()), start=start, end=end)["Close"]
        df.columns = self.tickers.keys()
        self.data = df.dropna()
        self.latest_yields = self.data.iloc[-1].to_dict()
        return self.data

    def analyze_yield_curve(self):
        short_term = self.latest_yields["13W"]
        long_term = self.latest_yields["30Y"]
        if short_term > long_term:
            return "inverted"
        elif abs(short_term - long_term) < 0.1:
            return "flat"
        else:
            return "normal"

    def detect_inversions(self):
        short_term = self.latest_yields["13W"]
        long_term = self.latest_yields["30Y"]
        return short_term > long_term

    def analyze_trend(self):
        # Analyze 10Y yield trend
        series = self.data["10Y"].dropna().values.reshape(-1, 1)
        x = np.arange(len(series)).reshape(-1, 1)
        model = LinearRegression().fit(x, series)
        slope = model.coef_[0][0]
        if slope > 0.01:
            return "rising"
        elif slope < -0.01:
            return "declining"
        else:
            return "flat"

    def run(self):
        self.fetch_data()
        curve = self.analyze_yield_curve()
        inversion = self.detect_inversions()
        trend = self.analyze_trend()
        summary = {
            "yield_curve": curve,
            "inversion_detected": inversion,
            "short_term_yield": round(self.latest_yields["13W"], 2),
            "long_term_yield": round(self.latest_yields["30Y"], 2),
            "rate_trend": trend,
            "insights": f"Yield curve is {curve}. Trend in 10Y yields is {trend}."
        }
        return summary
