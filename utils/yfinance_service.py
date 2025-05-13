import yfinance as yf

def get_stock_data(stock_symbol: str):
    """
    Fetch stock data from yfinance for the given stock symbol.
    
    Args:
        stock_symbol (str): The stock symbol (e.g., "MSFT").
        
    Returns:
        dict: A dictionary containing stock data.
    """
    # Fetch stock data
    stock_data = yf.Ticker(stock_symbol)
    current_price = stock_data.info.get("regularMarketPrice", 0)
    daily_change = stock_data.info.get("regularMarketChange", 0)
    
    if current_price == 0:
        raise ValueError("Invalid stock symbol or no data available.")
    
    return {
        "current_price": current_price,
        "daily_change": daily_change,
    }