from fastapi import FastAPI, Request
import models, schemas
from database.connection import engine
from routers import user, holdings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

models.Base.metadata.create_all(bind=engine)

# Set up rate limiter based on IP
limiter = Limiter(key_func=get_remote_address)

# Create the FastAPI app
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.middleware("http")
@limiter.limit("15/minute") # Limit to 15 requests per minute
async def global_rate_limiter(request: Request, call_next):
    return await call_next(request)


app.include_router(user.router)
app.include_router(holdings.router)

@app.get("/")
async def root():
    return {"message": "Welcome to FinSight-AI"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}