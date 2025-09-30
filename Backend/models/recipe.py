from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CookingMethod(str, Enum):
    BAKING = "baking"
    BOILING = "boiling"
    FRYING = "frying"
    GRILLING = "grilling"
    ROASTING = "roasting"
    STEAMING = "steaming"
    SAUTEING = "sauteing"
    BRAISING = "braising"
    SLOW_COOKING = "slow_cooking"
    RAW = "raw"


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    DESSERT = "dessert"
    APPETIZER = "appetizer"
    BEVERAGE = "beverage"


class RecipeIngredient(BaseModel):
    ingredient_id: str = Field(..., description="Reference to ingredient ID")
    quantity: float = Field(..., description="Amount needed")
    unit: str = Field(..., description="Unit of measurement")
    preparation: Optional[str] = None  # e.g., "chopped", "diced", "minced"
    is_optional: bool = Field(default=False)
    substitutes: List[str] = Field(default_factory=list, description="Alternative ingredient IDs")


class CookingStep(BaseModel):
    step_number: int = Field(..., description="Order of the step")
    instruction: str = Field(..., description="Detailed instruction")
    duration_minutes: Optional[int] = None
    temperature: Optional[str] = None  # e.g., "350°F", "medium heat"
    equipment: List[str] = Field(default_factory=list, description="Required equipment")
    tips: Optional[str] = None


class NutritionalSummary(BaseModel):
    total_calories: Optional[float] = None
    servings: int = Field(default=1)
    calories_per_serving: Optional[float] = None
    protein_per_serving: Optional[float] = None
    carbs_per_serving: Optional[float] = None
    fat_per_serving: Optional[float] = None
    fiber_per_serving: Optional[float] = None


class Recipe(BaseModel):
    id: str = Field(..., description="Unique identifier for the recipe")
    name: str = Field(..., description="Name of the recipe")
    description: Optional[str] = None
    cuisine: Optional[str] = None  # e.g., "Italian", "Mexican", "Asian"
    meal_types: List[MealType] = Field(default_factory=list)
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.INTERMEDIATE)
    cooking_methods: List[CookingMethod] = Field(default_factory=list)
    
    # Time information
    prep_time_minutes: int = Field(..., description="Preparation time in minutes")
    cook_time_minutes: int = Field(..., description="Cooking time in minutes")
    total_time_minutes: int = Field(..., description="Total time in minutes")
    
    # Ingredients and instructions
    ingredients: List[RecipeIngredient] = Field(..., description="List of required ingredients")
    instructions: List[CookingStep] = Field(..., description="Cooking instructions")
    
    # Serving and nutrition
    servings: int = Field(default=4, description="Number of servings")
    nutritional_summary: Optional[NutritionalSummary] = None
    
    # Tags and metadata
    dietary_tags: List[str] = Field(default_factory=list, description="Dietary restrictions/preferences")
    tags: List[str] = Field(default_factory=list, description="General tags")
    equipment_needed: List[str] = Field(default_factory=list, description="Required equipment")
    
    # Rating and popularity
    average_rating: Optional[float] = Field(None, ge=0, le=5, description="Average user rating (0-5)")
    rating_count: int = Field(default=0, description="Number of ratings")
    popularity_score: float = Field(default=0.0, description="Algorithm-calculated popularity")
    
    # Source and metadata
    source: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Algorithm-specific fields
    ingredient_complexity_score: Optional[float] = Field(None, description="Calculated complexity based on ingredients")
    technique_complexity_score: Optional[float] = Field(None, description="Calculated complexity based on techniques")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "pasta_tomato_001",
                "name": "Classic Tomato Pasta",
                "description": "A simple and delicious tomato pasta recipe",
                "cuisine": "Italian",
                "meal_types": ["lunch", "dinner"],
                "difficulty": "beginner",
                "cooking_methods": ["boiling", "sauteing"],
                "prep_time_minutes": 10,
                "cook_time_minutes": 20,
                "total_time_minutes": 30,
                "servings": 4,
                "ingredients": [
                    {
                        "ingredient_id": "pasta_001",
                        "quantity": 400,
                        "unit": "g",
                        "preparation": "any shape"
                    },
                    {
                        "ingredient_id": "tomato_001",
                        "quantity": 500,
                        "unit": "g",
                        "preparation": "chopped"
                    }
                ],
                "dietary_tags": ["vegetarian"],
                "tags": ["quick", "easy", "family-friendly"]
            }
        }


class RecipeMatch(BaseModel):
    recipe: Recipe
    match_score: float = Field(ge=0, le=1, description="How well this recipe matches the query")
    available_ingredients: List[str] = Field(description="Available ingredient IDs")
    missing_ingredients: List[str] = Field(description="Missing ingredient IDs")
    substitutable_ingredients: List[str] = Field(description="Ingredients that can be substituted")
    confidence_score: float = Field(ge=0, le=1, description="Confidence in the recommendation")
    algorithm_used: str = Field(description="Algorithm used for matching")
    reasoning: Optional[str] = None


class RecipeSuggestionRequest(BaseModel):
    available_ingredients: List[str] = Field(..., description="List of available ingredient IDs or names")
    dietary_preferences: List[str] = Field(default_factory=list, description="Dietary restrictions/preferences")
    meal_type: Optional[MealType] = None
    max_missing_ingredients: int = Field(default=3, description="Maximum number of missing ingredients allowed")
    max_prep_time: Optional[int] = Field(None, description="Maximum preparation time in minutes")
    max_cook_time: Optional[int] = Field(None, description="Maximum cooking time in minutes")
    difficulty_level: Optional[DifficultyLevel] = None
    cuisine_preference: Optional[str] = None
    exclude_ingredients: List[str] = Field(default_factory=list, description="Ingredients to avoid")
    algorithm_preference: Optional[str] = Field(None, description="Preferred algorithm: 'greedy', 'backtracking', or 'graph'")


class RecipeSuggestionResponse(BaseModel):
    matches: List[RecipeMatch] = Field(description="List of matching recipes")
    total_recipes_analyzed: int = Field(description="Total number of recipes analyzed")
    analysis_time_ms: float = Field(description="Time taken for analysis in milliseconds")
    algorithm_insights: Dict[str, Any] = Field(description="Insights from the algorithm used")
    ingredient_gap_analysis: Dict[str, Any] = Field(description="Analysis of missing ingredients")
    substitution_recommendations: List[Dict[str, Any]] = Field(description="Recommended substitutions") 