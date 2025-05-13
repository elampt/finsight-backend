from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Holding, Stock
from utils.yfinance_service import get_stock_data

def calculate_portfolio(db: Session, user_id: int):
    # Fetch aggregated holdings
    holdings = (
        db.query(
            Stock.stock_symbol,
            Stock.stock_name,
            func.sum(Holding.purchase_cost).label("total_cost"),
            func.sum(Holding.shares).label("total_shares")
        )
        .join(Stock, Stock.id == Holding.stock_id)
        .filter(Holding.user_id == user_id)
        .group_by(Holding.stock_id, Stock.stock_symbol, Stock.stock_name)
        .all()
    )

    result = []
    total_portfolio_cost = 0
    total_portfolio_value = 0

    for holding in holdings:
        stock_symbol = holding.stock_symbol
        total_cost = holding.total_cost
        total_shares = holding.total_shares

        # Fetch individual purchases for the stock
        purchases = (
            db.query(Holding)
            .join(Stock, Stock.id == Holding.stock_id)
            .filter(Holding.user_id == user_id, Stock.stock_symbol == stock_symbol)
            .all()
        )

        # Fetch current stock data using yfinance service
        stock_data = get_stock_data(stock_symbol)
        current_price = stock_data["current_price"]
        daily_change = stock_data["daily_change"]

        # Calculate profit/loss
        market_value = current_price * total_shares
        total_profit_loss = market_value - total_cost
        daily_profit_loss = daily_change * total_shares

        # Calculate profit/loss percentage
        total_profit_loss_percentage = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0
        daily_profit_loss_percentage = (daily_profit_loss / total_cost) * 100 if total_cost > 0 else 0

        # Add individual purchase breakdown
        purchase_breakdown = [
            {
                "holding_id": purchase.id,  # Include the holding ID in the purchase breakdown
                "purchase_cost": round(purchase.purchase_cost, 2),
                "shares": round(purchase.shares, 2),
                "purchase_date": purchase.purchase_date
            }
            for purchase in purchases
        ]

        # Append to result
        result.append({
            "stock_symbol": stock_symbol,
            "stock_name": holding.stock_name,
            "total_cost": round(total_cost, 2),
            "total_shares": round(total_shares, 2),
            "current_price": round(current_price, 2),
            "market_value": round(market_value, 2),
            "total_profit_loss": round(total_profit_loss, 2),
            "total_profit_loss_percentage": round(total_profit_loss_percentage, 2),
            "daily_profit_loss": round(daily_profit_loss, 2),
            "daily_profit_loss_percentage": round(daily_profit_loss_percentage, 2),
            "purchases": purchase_breakdown  # Include the purchase breakdown here
        })

        # Update portfolio totals
        total_portfolio_cost += total_cost
        total_portfolio_value += market_value

    # Calculate portfolio profit/loss
    total_portfolio_profit_loss = total_portfolio_value - total_portfolio_cost
    total_portfolio_profit_loss_percentage = (total_portfolio_profit_loss / total_portfolio_cost) * 100 if total_portfolio_cost > 0 else 0

    # Portfolio summary
    portfolio_summary = {
        "total_cost": round(total_portfolio_cost, 2),
        "total_value": round(total_portfolio_value, 2),
        "total_profit_loss": round(total_portfolio_profit_loss, 2),
        "total_profit_loss_percentage": round(total_portfolio_profit_loss_percentage, 2)
    }

    return {
        "portfolio_summary": portfolio_summary,
        "holdings": result
    }