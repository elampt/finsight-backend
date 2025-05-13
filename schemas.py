from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import date

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class HoldingCreate(BaseModel):
    stock_symbol: str
    shares: float
    purchase_cost: float
    purchase_date: date

class HoldingCreateResponse(BaseModel):
    id: int
    shares: float
    purchase_cost: float
    purchase_date: date

    class Config:
        from_attributes = True

# class HoldingSummary(BaseModel):
#     stock_symbol: str
#     stock_name: str
#     total_cost: float
#     total_shares: float

#     class Config:
#         from_attributes = True

class HoldingResponse(BaseModel):
    id: int
    stock_symbol: str
    shares: float
    purchase_cost: float
    purchase_date: date

    class Config:
        from_attributes = True

class HoldingUpdate(BaseModel):
    shares: Optional[float] = None
    purchase_cost: Optional[float] = None
    purchase_date: Optional[date] = None

class PurchaseBreakdown(BaseModel):
    holding_id: int
    purchase_cost: float
    shares: float
    purchase_date: date

class HoldingProfitLoss(BaseModel):
    stock_symbol: str
    stock_name: str
    total_cost: float
    total_shares: float
    current_price: float
    market_value: float
    total_profit_loss: float
    total_profit_loss_percentage: float
    daily_profit_loss: float
    daily_profit_loss_percentage: float
    purchases: List[PurchaseBreakdown] 

    class Config:
        from_attributes = True

class PortfolioSummary(BaseModel):
    total_cost: float
    total_value: float
    total_profit_loss: float
    total_profit_loss_percentage: float

class PortfolioResponse(BaseModel):
    portfolio_summary: PortfolioSummary
    holdings: List[HoldingProfitLoss]

class ArticleSentiment(BaseModel):
    title: str
    publisher: str
    link: str
    sentiment: str
    confidence: float

class StockSentiment(BaseModel):
    stock_symbol: str
    stock_name: str
    sentiment_summary: Dict[str, int]
    related_articles: List[ArticleSentiment]

class NewsSentimentResponse(BaseModel):
    overall_sentiment_summary: Dict[str, int]
    holdings_sentiment: List[StockSentiment]