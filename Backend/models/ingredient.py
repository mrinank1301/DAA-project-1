from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class IngredientCategory(str, Enum):
    PROTEIN = "protein"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    GRAIN = "grain"
    DAIRY = "dairy"
    SPICE = "spice"
    HERB = "herb"
    CONDIMENT = "condiment"
    FAT = "fat"
    LIQUID = "liquid"
    SWEETENER = "sweetener"
    NUTS_SEEDS = "nuts_seeds"


class NutritionalInfo(BaseModel):
    calories_per_100g: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    sugar_g: Optional[float] = None
    sodium_mg: Optional[float] = None


class FlavorProfile(BaseModel):
    sweetness: float = Field(ge=0, le=10, description="Sweetness level (0-10)")
    saltiness: float = Field(ge=0, le=10, description="Saltiness level (0-10)")
    sourness: float = Field(ge=0, le=10, description="Sourness level (0-10)")
    bitterness: float = Field(ge=0, le=10, description="Bitterness level (0-10)")
    umami: float = Field(ge=0, le=10, description="Umami level (0-10)")
    spiciness: float = Field(ge=0, le=10, description="Spiciness level (0-10)")


class Ingredient(BaseModel):
    id: str = Field(..., description="Unique identifier for the ingredient")
    name: str = Field(..., description="Name of the ingredient")
    category: IngredientCategory
    aliases: List[str] = Field(default_factory=list, description="Alternative names")
    flavor_profile: FlavorProfile
    nutritional_info: NutritionalInfo = Field(default_factory=NutritionalInfo)
    common_substitutes: List[str] = Field(default_factory=list, description="Common substitute ingredient IDs")
    dietary_tags: List[str] = Field(default_factory=list, description="Dietary restrictions/tags")
    storage_info: Optional[str] = None
    season: Optional[List[str]] = Field(default_factory=list, description="Seasonal availability")
    origin: Optional[str] = None
    cost_level: Optional[int] = Field(None, ge=1, le=5, description="Cost level (1-5, 1=cheap, 5=expensive)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "tomato_001",
                "name": "Tomato",
                "category": "vegetable",
                "aliases": ["tomatoes", "fresh tomato"],
                "flavor_profile": {
                    "sweetness": 6,
                    "saltiness": 1,
                    "sourness": 4,
                    "bitterness": 1,
                    "umami": 7,
                    "spiciness": 0
                },
                "nutritional_info": {
                    "calories_per_100g": 18,
                    "protein_g": 0.9,
                    "carbs_g": 3.9,
                    "fat_g": 0.2
                },
                "common_substitutes": ["canned_tomato_001", "tomato_paste_001"],
                "dietary_tags": ["vegetarian", "vegan", "gluten-free"],
                "season": ["summer", "fall"],
                "cost_level": 2
            }
        }


class IngredientSubstitution(BaseModel):
    original_ingredient_id: str
    substitute_ingredient_id: str
    substitution_ratio: float = Field(default=1.0, description="Ratio for substitution (e.g., 1.5 means use 1.5x amount)")
    compatibility_score: float = Field(ge=0, le=1, description="How well this substitution works (0-1)")
    flavor_impact: str = Field(description="Description of flavor changes")
    notes: Optional[str] = None


class IngredientCompatibility(BaseModel):
    ingredient1_id: str
    ingredient2_id: str
    compatibility_score: float = Field(ge=0, le=1, description="Compatibility score (0-1)")
    relationship_type: str = Field(description="Type of relationship (complementary, neutral, conflicting)")
    common_dishes: List[str] = Field(default_factory=list, description="Common dishes using both ingredients") 