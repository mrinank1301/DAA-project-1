from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
import logging

from models.recipe import (
    Recipe, RecipeSuggestionRequest, RecipeSuggestionResponse, 
    MealType, DifficultyLevel
)
from models.ingredient import Ingredient, IngredientCategory
from services.recipe_service import RecipeRecommendationService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global service instance (in production, use dependency injection)
recipe_service = RecipeRecommendationService()


@router.post("/recipes/suggest", response_model=RecipeSuggestionResponse)
async def suggest_recipes(request: RecipeSuggestionRequest):
    """
    Get recipe suggestions based on available ingredients using algorithmic analysis.
    
    This endpoint uses graph theory, backtracking, and greedy algorithms to find
    the best recipe matches based on your available ingredients.
    """
    try:
        response = recipe_service.suggest_recipes(request)
        return response
    except Exception as e:
        logger.error(f"Error in suggest_recipes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/recipes/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: str):
    """
    Get detailed information about a specific recipe.
    """
    recipe = recipe_service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.get("/recipes", response_model=List[Recipe])
async def list_recipes(
    limit: int = Query(20, ge=1, le=100, description="Number of recipes to return"),
    offset: int = Query(0, ge=0, description="Number of recipes to skip"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    meal_type: Optional[MealType] = Query(None, description="Filter by meal type"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    max_prep_time: Optional[int] = Query(None, ge=1, description="Maximum preparation time in minutes"),
    dietary_tags: Optional[List[str]] = Query(None, description="Filter by dietary tags")
):
    """
    List recipes with optional filtering.
    """
    try:
        recipes = list(recipe_service.recipes.values())
        
        # Apply filters
        if cuisine:
            recipes = [r for r in recipes if r.cuisine and r.cuisine.lower() == cuisine.lower()]
        
        if meal_type:
            recipes = [r for r in recipes if meal_type in r.meal_types]
        
        if difficulty:
            recipes = [r for r in recipes if r.difficulty == difficulty]
        
        if max_prep_time:
            recipes = [r for r in recipes if r.prep_time_minutes <= max_prep_time]
        
        if dietary_tags:
            dietary_tags_lower = [tag.lower() for tag in dietary_tags]
            recipes = [
                r for r in recipes 
                if all(tag in [rt.lower() for rt in r.dietary_tags] for tag in dietary_tags_lower)
            ]
        
        # Apply pagination
        total_recipes = len(recipes)
        recipes = recipes[offset:offset + limit]
        
        return recipes
        
    except Exception as e:
        logger.error(f"Error in list_recipes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/ingredients/analyze")
async def analyze_ingredients(request: RecipeSuggestionRequest):
    """
    Analyze ingredient gaps and get substitution recommendations without full recipe suggestions.
    """
    try:
        # Get a limited set of matches for analysis
        limited_request = RecipeSuggestionRequest(
            available_ingredients=request.available_ingredients,
            dietary_preferences=request.dietary_preferences,
            max_missing_ingredients=request.max_missing_ingredients
        )
        
        response = recipe_service.suggest_recipes(limited_request)
        
        # Return only the analysis parts
        return {
            "ingredient_gap_analysis": response.ingredient_gap_analysis,
            "substitution_recommendations": response.substitution_recommendations,
            "analysis_time_ms": response.analysis_time_ms,
            "total_recipes_analyzed": response.total_recipes_analyzed
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_ingredients: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/ingredients/{ingredient_id}/substitutes")
async def get_ingredient_substitutes(ingredient_id: str, available_ingredients: List[str] = Query(...)):
    """
    Get substitution recommendations for a specific ingredient.
    """
    try:
        ingredient = recipe_service.get_ingredient_by_id(ingredient_id)
        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        
        available_set = set(available_ingredients)
        substitutes = recipe_service.ingredient_graph.find_ingredient_substitutes(
            ingredient_id, available_set
        )
        
        substitutes_info = []
        for substitute_id, similarity_score in substitutes:
            substitute_ingredient = recipe_service.get_ingredient_by_id(substitute_id)
            if substitute_ingredient:
                substitutes_info.append({
                    "ingredient": substitute_ingredient,
                    "similarity_score": similarity_score,
                    "substitution_notes": recipe_service._generate_substitution_notes(ingredient_id, substitute_id)
                })
        
        return {
            "original_ingredient": ingredient,
            "substitutes": substitutes_info,
            "total_substitutes_found": len(substitutes_info)
        }
        
    except Exception as e:
        logger.error(f"Error in get_ingredient_substitutes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/ingredients/{ingredient_id}", response_model=Ingredient)
async def get_ingredient(ingredient_id: str):
    """
    Get detailed information about a specific ingredient.
    """
    ingredient = recipe_service.get_ingredient_by_id(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.get("/ingredients", response_model=List[Ingredient])
async def list_ingredients(
    limit: int = Query(50, ge=1, le=200, description="Number of ingredients to return"),
    offset: int = Query(0, ge=0, description="Number of ingredients to skip"),
    category: Optional[IngredientCategory] = Query(None, description="Filter by ingredient category"),
    dietary_tags: Optional[List[str]] = Query(None, description="Filter by dietary tags"),
    search: Optional[str] = Query(None, description="Search by ingredient name")
):
    """
    List ingredients with optional filtering and search.
    """
    try:
        ingredients = list(recipe_service.ingredients.values())
        
        # Apply filters
        if category:
            ingredients = [i for i in ingredients if i.category == category]
        
        if dietary_tags:
            dietary_tags_lower = [tag.lower() for tag in dietary_tags]
            ingredients = [
                i for i in ingredients 
                if all(tag in [it.lower() for it in i.dietary_tags] for tag in dietary_tags_lower)
            ]
        
        if search:
            search_lower = search.lower()
            ingredients = [
                i for i in ingredients 
                if (search_lower in i.name.lower() or 
                    any(search_lower in alias.lower() for alias in i.aliases))
            ]
        
        # Apply pagination
        ingredients = ingredients[offset:offset + limit]
        
        return ingredients
        
    except Exception as e:
        logger.error(f"Error in list_ingredients: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/graph/analyze")
async def analyze_graph(available_ingredients: List[str]):
    """
    Get graph-based analysis of ingredient relationships and recipe networks.
    """
    try:
        available_set = set(available_ingredients)
        
        # Get graph statistics
        graph_stats = recipe_service.ingredient_graph.get_graph_statistics()
        
        # Get ingredient centrality (importance in the network)
        centrality = recipe_service.ingredient_graph.get_ingredient_centrality()
        
        # Find recipe clusters
        clusters = recipe_service.ingredient_graph.find_recipe_clusters()
        
        # Analyze available ingredients
        available_analysis = {}
        for ingredient_name in available_ingredients:
            # Normalize ingredient name to ID
            normalized_ids = recipe_service._normalize_ingredient_identifiers({ingredient_name})
            for ingredient_id in normalized_ids:
                if ingredient_id in centrality:
                    available_analysis[ingredient_name] = {
                        "ingredient_id": ingredient_id,
                        "centrality_score": centrality[ingredient_id],
                        "importance_rank": "high" if centrality[ingredient_id] > 0.1 else "medium" if centrality[ingredient_id] > 0.05 else "low"
                    }
        
        return {
            "graph_statistics": graph_stats,
            "ingredient_centrality": dict(list(sorted(centrality.items(), key=lambda x: x[1], reverse=True))[:20]),
            "recipe_clusters": clusters,
            "available_ingredients_analysis": available_analysis,
            "recommendations": {
                "key_missing_ingredients": [
                    {"ingredient_id": ing_id, "centrality": score, "name": recipe_service.ingredients.get(ing_id, {}).name if ing_id in recipe_service.ingredients else ing_id}
                    for ing_id, score in sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
                    if ing_id not in recipe_service._normalize_ingredient_identifiers(available_set)
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/recipes/quick")
async def get_quick_recipes(
    available_ingredients: List[str] = Query(..., description="Available ingredients"),
    max_time_minutes: int = Query(30, ge=5, le=120, description="Maximum total time in minutes"),
    max_results: int = Query(5, ge=1, le=20, description="Maximum number of results")
):
    """
    Get quick recipe suggestions using greedy algorithm optimized for speed.
    """
    try:
        available_set = recipe_service._normalize_ingredient_identifiers(set(available_ingredients))
        matches = recipe_service.greedy_matcher.find_quick_recipes(
            available_set, max_time_minutes, max_results
        )
        
        return {
            "matches": matches,
            "algorithm_used": "greedy_time_optimized",
            "max_time_constraint": max_time_minutes,
            "total_matches_found": len(matches)
        }
        
    except Exception as e:
        logger.error(f"Error in get_quick_recipes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/recipes/popular")
async def get_popular_recipes(
    available_ingredients: List[str] = Query(..., description="Available ingredients"),
    max_results: int = Query(5, ge=1, le=20, description="Maximum number of results")
):
    """
    Get popular recipe suggestions that can be made with available ingredients.
    """
    try:
        available_set = recipe_service._normalize_ingredient_identifiers(set(available_ingredients))
        matches = recipe_service.greedy_matcher.find_recipes_by_popularity(
            available_set, max_results
        )
        
        return {
            "matches": matches,
            "algorithm_used": "greedy_popularity_based",
            "total_matches_found": len(matches)
        }
        
    except Exception as e:
        logger.error(f"Error in get_popular_recipes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/system/stats")
async def get_system_statistics():
    """
    Get system statistics including algorithm performance and data metrics.
    """
    try:
        stats = recipe_service.get_system_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error in get_system_statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/recipes", response_model=Recipe)
async def add_recipe(recipe: Recipe):
    """
    Add a new recipe to the system.
    """
    try:
        recipe_service.add_recipe(recipe)
        return recipe
        
    except Exception as e:
        logger.error(f"Error in add_recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/ingredients", response_model=Ingredient)
async def add_ingredient(ingredient: Ingredient):
    """
    Add a new ingredient to the system.
    """
    try:
        recipe_service.add_ingredient(ingredient)
        return ingredient
        
    except Exception as e:
        logger.error(f"Error in add_ingredient: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "FlavorGraph API",
        "algorithms": {
            "graph_theory": "available",
            "backtracking": "available", 
            "greedy": "available"
        },
        "data": {
            "recipes_loaded": len(recipe_service.recipes),
            "ingredients_loaded": len(recipe_service.ingredients)
        }
    } 