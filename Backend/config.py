"""
Configuration settings for FlavorGraph.
"""

import os
from typing import Dict, Any


class Config:
    """Base configuration class."""
    
    # Server settings
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # Algorithm settings
    DEFAULT_ALGORITHM = os.getenv("DEFAULT_ALGORITHM", "graph")  # graph, greedy, backtracking
    MAX_RECIPE_RESULTS = int(os.getenv("MAX_RECIPE_RESULTS", 10))
    MAX_SUBSTITUTION_RESULTS = int(os.getenv("MAX_SUBSTITUTION_RESULTS", 5))
    
    # Performance settings
    BACKTRACKING_MAX_EXPLORATIONS = int(os.getenv("BACKTRACKING_MAX_EXPLORATIONS", 10000))
    GRAPH_CENTRALITY_CACHE_TTL = int(os.getenv("GRAPH_CENTRALITY_CACHE_TTL", 3600))  # seconds
    
    # Scoring thresholds
    MIN_RECIPE_MATCH_SCORE = float(os.getenv("MIN_RECIPE_MATCH_SCORE", 0.1))
    MIN_SUBSTITUTION_SIMILARITY = float(os.getenv("MIN_SUBSTITUTION_SIMILARITY", 0.3))
    
    # Algorithm selection thresholds
    GREEDY_RECIPE_THRESHOLD = int(os.getenv("GREEDY_RECIPE_THRESHOLD", 1000))  # Use greedy if more recipes
    GREEDY_INGREDIENT_THRESHOLD = int(os.getenv("GREEDY_INGREDIENT_THRESHOLD", 20))  # Use greedy if more ingredients
    BACKTRACKING_RECIPE_THRESHOLD = int(os.getenv("BACKTRACKING_RECIPE_THRESHOLD", 100))  # Use backtracking if fewer recipes
    BACKTRACKING_INGREDIENT_THRESHOLD = int(os.getenv("BACKTRACKING_INGREDIENT_THRESHOLD", 10))  # Use backtracking if fewer ingredients
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # CORS settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS = ["*"]
    
    # API settings
    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
    API_TITLE = "FlavorGraph: Intelligent Recipe Navigator"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = """
    FlavorGraph is an intelligent recipe recommendation system that leverages graph theory, 
    backtracking, and greedy algorithms to suggest recipes based on available ingredients, 
    provide ingredient gap analysis, and offer substitution recommendations.
    """
    
    # Feature flags
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "false").lower() == "true"
    ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "false").lower() == "true"
    ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true"
    
    @classmethod
    def get_algorithm_config(cls) -> Dict[str, Any]:
        """Get algorithm-specific configuration."""
        return {
            "default_algorithm": cls.DEFAULT_ALGORITHM,
            "backtracking": {
                "max_explorations": cls.BACKTRACKING_MAX_EXPLORATIONS,
                "use_threshold": {
                    "max_recipes": cls.BACKTRACKING_RECIPE_THRESHOLD,
                    "max_ingredients": cls.BACKTRACKING_INGREDIENT_THRESHOLD
                }
            },
            "greedy": {
                "use_threshold": {
                    "min_recipes": cls.GREEDY_RECIPE_THRESHOLD,
                    "min_ingredients": cls.GREEDY_INGREDIENT_THRESHOLD
                }
            },
            "graph": {
                "centrality_cache_ttl": cls.GRAPH_CENTRALITY_CACHE_TTL
            }
        }
    
    @classmethod
    def get_scoring_config(cls) -> Dict[str, float]:
        """Get scoring thresholds configuration."""
        return {
            "min_recipe_match_score": cls.MIN_RECIPE_MATCH_SCORE,
            "min_substitution_similarity": cls.MIN_SUBSTITUTION_SIMILARITY
        }
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """Get API configuration."""
        return {
            "title": cls.API_TITLE,
            "version": cls.API_VERSION,
            "description": cls.API_DESCRIPTION,
            "prefix": cls.API_PREFIX,
            "cors": {
                "origins": cls.CORS_ORIGINS,
                "methods": cls.CORS_METHODS,
                "headers": cls.CORS_HEADERS
            }
        }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    ENABLE_CACHING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    HOST = "0.0.0.0"
    ENABLE_CACHING = True
    ENABLE_ANALYTICS = True
    ENABLE_RATE_LIMITING = True


class TestConfig(Config):
    """Test configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    MAX_RECIPE_RESULTS = 5
    BACKTRACKING_MAX_EXPLORATIONS = 1000


# Configuration mapping
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "test": TestConfig
}


def get_config(env: str = None) -> Config:
    """Get configuration based on environment."""
    if env is None:
        env = os.getenv("FLASK_ENV", "development")
    
    return config_map.get(env, DevelopmentConfig) 