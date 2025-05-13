from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Holding, Stock, User
from database.connection import get_db
from auth.jwt import get_current_user
import schemas
from utils.yfinance_service import get_stock_data
from utils.portfolio_service import calculate_portfolio
from utils.sentiment_service import fetch_news, analyze_sentiment


router = APIRouter(prefix="/holdings", tags=["Holdings"])

@router.post("/add", response_model=schemas.HoldingCreateResponse, status_code=201)
async def add_holding(holding: schemas.HoldingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stock = db.query(Stock).filter(Stock.stock_symbol == holding.stock_symbol).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    new_holding = Holding(
        user_id=current_user.id,
        stock_id=stock.id,
        shares=holding.shares,
        purchase_cost=holding.purchase_cost,
        purchase_date=holding.purchase_date
    )
    db.add(new_holding)
    db.commit()
    db.refresh(new_holding)
    return new_holding


@router.get("/by-symbol", response_model=list[schemas.HoldingResponse])
async def get_holdings_by_symbol(stock_symbol: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    holdings = (
        db.query(Holding, Stock.stock_symbol)
        .join(Stock, Stock.id == Holding.stock_id)
        .filter(Holding.user_id == current_user.id, Stock.stock_symbol == stock_symbol)
        .all()
    )
    if not holdings:
        raise HTTPException(status_code=404, detail="No holdings found for this stock symbol")
    return [
        {
            "id": holding.Holding.id,
            "stock_symbol": holding.stock_symbol,
            "shares": holding.Holding.shares,
            "purchase_cost": holding.Holding.purchase_cost,
            "purchase_date": holding.Holding.purchase_date
        }
        for holding in holdings
    ]


@router.get("/profit-loss", response_model=schemas.PortfolioResponse)
async def get_holdings_profit_loss(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        portfolio_data = calculate_portfolio(db, current_user.id)
        return portfolio_data
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{holding_id}", status_code=204)
async def delete_holding(holding_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a holding by ID.
    """
    holding = db.query(Holding).filter(Holding.id == holding_id, Holding.user_id == current_user.id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    db.delete(holding)
    db.commit()
    return {"detail": "Holding deleted successfully"}


@router.put("/update/{holding_id}", response_model=schemas.HoldingUpdate)
async def update_holding(holding_id: int, holding_data: schemas.HoldingUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update a holding by its ID.
    """
    holding = db.query(Holding).filter(Holding.id == holding_id, Holding.user_id == current_user.id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    # Update only the fields provided in the request body
    if holding_data.shares is not None:
        holding.shares = holding_data.shares
    if holding_data.purchase_cost is not None:
        holding.purchase_cost = holding_data.purchase_cost
    if holding_data.purchase_date is not None:
        holding.purchase_date = holding_data.purchase_date

    db.commit()
    db.refresh(holding)
    return holding


@router.get("/stocks/symbols", response_model=list[str])
async def get_stock_symbols(db: Session = Depends(get_db)):
    """
    Fetch all unique stock symbols from the user's holdings.
    """
    stock_symbols = db.query(Stock.stock_symbol).all()
    return [stock[0] for stock in stock_symbols]


@router.get("/news-sentiment", response_model=schemas.NewsSentimentResponse)
async def get_news_sentiment(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Fetch news articles and perform sentiment analysis for the user's holdings.
    """
    # Fetch the user's unique holdings
    unique_stocks = (
        db.query(Stock.stock_symbol, Stock.stock_name)
        .join(Holding, Stock.id == Holding.stock_id)
        .filter(Holding.user_id == current_user.id)
        .distinct()
        .all()
    )

    result = []
    overall_sentiment_summary = {"positive": 0, "negative": 0, "neutral": 0}

    for stock in unique_stocks:
        stock_symbol = stock.stock_symbol
        stock_name = stock.stock_name

        try:
            # Fetch news and perform sentiment analysis
            news_articles = fetch_news(stock_symbol)
            if not news_articles:
                print(f"No news found for {stock_symbol}")
                continue  # Skip if no news articles are found

            analyzed_articles, sentiment_summary = analyze_sentiment(news_articles)

            stock_data = {
                "stock_symbol": stock_symbol,
                "stock_name": stock_name,
                "sentiment_summary": sentiment_summary,
                "related_articles": analyzed_articles
            }

        except Exception as e:
            print(f"Error processing {stock_symbol}: {e}")
            continue  # Skip this stock if an error occurs

        # Update overall sentiment summary
        for sentiment, count in stock_data["sentiment_summary"].items():
            overall_sentiment_summary[sentiment] += count

        result.append(stock_data)

    return {
        "overall_sentiment_summary": overall_sentiment_summary,
        "holdings_sentiment": result
    }

