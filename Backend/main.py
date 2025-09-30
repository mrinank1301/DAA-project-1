from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from contextlib import asynccontextmanager

from api.routes import router
from data.sample_data import load_sample_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting FlavorGraph API...")
    
    # Load sample data
    try:
        await load_sample_data()
        logger.info("Sample data loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load sample data: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FlavorGraph API...")


# Create FastAPI application
app = FastAPI(
    title="FlavorGraph: Intelligent Recipe Navigator",
    description="""
    FlavorGraph is an intelligent recipe recommendation system that leverages graph theory, 
    backtracking, and greedy algorithms to suggest recipes based on available ingredients, 
    provide ingredient gap analysis, and offer substitution recommendations.
    
    ## Features
    
    * **Graph-based Recipe Matching**: Uses graph theory to model ingredient relationships
    * **Intelligent Recipe Suggestions**: Employs backtracking and greedy algorithms for optimal recommendations
    * **Ingredient Gap Analysis**: Identifies missing ingredients and suggests alternatives
    * **Substitution Engine**: Recommends ingredient substitutions based on flavor profiles
    * **Algorithmic Insights**: Provides detailed analysis of recommendation decisions
    
    ## Algorithms
    
    * **Graph Theory**: Models ingredients and recipes as nodes with weighted edges
    * **Backtracking Algorithm**: Explores all possible recipe combinations for optimal matches
    * **Greedy Algorithm**: Provides fast, near-optimal suggestions for real-time recommendations
    
    ## Usage
    
    1. Use `/recipes/suggest` for comprehensive recipe recommendations
    2. Use `/recipes/quick` for fast suggestions with time constraints
    3. Use `/ingredients/analyze` for ingredient gap analysis
    4. Use `/graph/analyze` for network-based ingredient relationship analysis
    """,
    version="1.0.0",
    contact={
        "name": "FlavorGraph Team",
        "email": "support@flavorgraph.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
            "path": str(request.url)
        }
    )


# Include routes
app.include_router(router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to FlavorGraph: Intelligent Recipe Navigator",
        "version": "1.0.0",
        "description": "AI-powered recipe recommendations using graph theory, backtracking, and greedy algorithms",
        "documentation": "/docs",
        "health_check": "/api/v1/health",
        "algorithms": {
            "graph_theory": "Network-based ingredient relationship analysis",
            "backtracking": "Exhaustive search for optimal recipe matches", 
            "greedy": "Fast heuristic-based recommendations"
        },
        "key_endpoints": {
            "suggest_recipes": "/api/v1/recipes/suggest",
            "analyze_ingredients": "/api/v1/ingredients/analyze",
            "graph_analysis": "/api/v1/graph/analyze",
            "quick_recipes": "/api/v1/recipes/quick",
            "popular_recipes": "/api/v1/recipes/popular"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 