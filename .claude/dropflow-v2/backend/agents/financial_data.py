#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Data Integration
Real-time stock data and financial metrics
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FinancialDataFetcher:
    """
    Fetch real-time financial data from multiple sources
    Supports stocks, crypto, commodities, and economic indicators
    """

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.av_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.fmp_api_key = os.getenv('FMP_API_KEY')

    async def get_stock_price(
        self,
        symbol: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get current stock price and basic metrics
        Supports US stocks (e.g., AAPL, MSFT, TSLA)
        """
        # Check cache
        if use_cache and symbol in self.cache:
            cached_data, timestamp = self.cache[symbol]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                logger.info(f"[CACHE HIT] {symbol}")
                return cached_data

        try:
            # Use Yahoo Finance fallback (free, no API key needed)
            data = await self._fetch_yahoo_finance(symbol)

            if data:
                self.cache[symbol] = (data, datetime.now())
                return data

        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")

        return {
            "symbol": symbol,
            "price": 0.0,
            "change": 0.0,
            "change_percent": 0.0,
            "error": "Failed to fetch data"
        }

    async def _fetch_yahoo_finance(self, symbol: str) -> Optional[Dict]:
        """
        Fetch from Yahoo Finance using yfinance library
        Free alternative to paid APIs
        """
        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')

            if data.empty:
                return None

            current_price = data['Close'].iloc[-1]
            prev_price = data['Open'].iloc[-1]

            return {
                "symbol": symbol,
                "price": float(current_price),
                "previous_close": float(prev_price),
                "change": float(current_price - prev_price),
                "change_percent": float((current_price / prev_price - 1) * 100),
                "timestamp": datetime.now().isoformat(),
                "source": "yahoo_finance"
            }
        except ImportError:
            logger.warning("yfinance not installed. Install with: pip install yfinance")
            return None
        except Exception as e:
            logger.error(f"Yahoo Finance fetch error: {e}")
            return None

    async def get_multiple_stocks(
        self,
        symbols: List[str]
    ) -> Dict[str, Dict]:
        """Get prices for multiple stocks"""
        results = {}
        for symbol in symbols:
            results[symbol] = await self.get_stock_price(symbol)
        return results

    async def get_stock_trend(
        self,
        symbol: str,
        period: str = "1mo"
    ) -> Dict[str, Any]:
        """
        Get stock trend data for period
        period: 1d, 1wk, 1mo, 3mo, 1y
        """
        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)

            if data.empty:
                return {"error": "No data available"}

            prices = data['Close'].tolist()
            high = max(prices)
            low = min(prices)
            avg = sum(prices) / len(prices)

            return {
                "symbol": symbol,
                "period": period,
                "high": float(high),
                "low": float(low),
                "average": float(avg),
                "current": float(prices[-1]),
                "trend": "up" if prices[-1] > prices[0] else "down",
                "volatility": float((max(prices) - min(prices)) / avg * 100),
                "data_points": len(prices)
            }
        except Exception as e:
            logger.error(f"Error fetching trend for {symbol}: {e}")
            return {"error": str(e)}

    async def analyze_portfolio(
        self,
        holdings: Dict[str, float]  # {symbol: quantity}
    ) -> Dict[str, Any]:
        """
        Analyze portfolio composition and value
        holdings: {"AAPL": 10, "MSFT": 5}
        """
        results = []
        total_value = 0.0

        for symbol, quantity in holdings.items():
            price_data = await self.get_stock_price(symbol)
            value = price_data.get("price", 0.0) * quantity
            total_value += value

            results.append({
                "symbol": symbol,
                "quantity": quantity,
                "price": price_data.get("price"),
                "value": value,
                "percentage": 0.0  # Will calculate below
            })

        # Calculate percentages
        for item in results:
            item["percentage"] = (item["value"] / total_value * 100) if total_value > 0 else 0

        return {
            "holdings": results,
            "total_value": total_value,
            "timestamp": datetime.now().isoformat()
        }

    async def get_market_data(self) -> Dict[str, Any]:
        """Get major market indices"""
        indices = {
            "^GSPC": "S&P 500",
            "^IXIC": "NASDAQ",
            "^DJI": "Dow Jones"
        }

        data = {}
        for symbol, name in indices.items():
            price_data = await self.get_stock_price(symbol)
            if "error" not in price_data:
                data[name] = price_data

        return {
            "indices": data,
            "timestamp": datetime.now().isoformat()
        }

    def clear_cache(self) -> None:
        """Clear price cache"""
        self.cache.clear()
        logger.info("Cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cached_symbols": len(self.cache),
            "cache_ttl_seconds": self.cache_ttl,
            "symbols": list(self.cache.keys())
        }


# Quick start
if __name__ == "__main__":
    import asyncio

    async def demo():
        fetcher = FinancialDataFetcher()

        print("[DEMO] Fetching stock data...\n")

        # Single stock
        apple = await fetcher.get_stock_price("AAPL")
        print(f"Apple: ${apple.get('price'):.2f} ({apple.get('change_percent'):+.2f}%)")

        # Multiple stocks
        print("\n[DEMO] Portfolio Analysis\n")
        portfolio = await fetcher.analyze_portfolio({
            "AAPL": 10,
            "MSFT": 5,
            "GOOGL": 2
        })
        print(f"Total Portfolio Value: ${portfolio['total_value']:.2f}")
        for holding in portfolio['holdings']:
            print(f"  {holding['symbol']}: ${holding['value']:.2f} ({holding['percentage']:.1f}%)")

        # Market indices
        print("\n[DEMO] Market Indices\n")
        market = await fetcher.get_market_data()
        for name, data in market['indices'].items():
            print(f"{name}: {data.get('price'):.2f}")

    asyncio.run(demo())
