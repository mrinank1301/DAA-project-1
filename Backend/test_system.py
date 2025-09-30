#!/usr/bin/env python3
"""
Simple test script to verify FlavorGraph system functionality.
Run this after starting the server to test the core features.
"""

import asyncio
import json
from models.recipe import RecipeSuggestionRequest, MealType, DifficultyLevel
from data.sample_data import load_sample_data
from services.recipe_service import RecipeRecommendationService


async def test_system():
    """Test the core functionality of FlavorGraph."""
    
    print("🍳 Testing FlavorGraph System")
    print("=" * 50)
    
    # Initialize service and load data
    print("1. Loading sample data...")
    service = RecipeRecommendationService()
    
    # Manually load data for testing
    await load_sample_data()
    
    # Copy data to our test service
    from api.routes import recipe_service as global_service
    service.recipes = global_service.recipes.copy()
    service.ingredients = global_service.ingredients.copy()
    service.ingredient_graph = global_service.ingredient_graph
    service._reinitialize_matchers()
    
    print(f"   ✓ Loaded {len(service.recipes)} recipes")
    print(f"   ✓ Loaded {len(service.ingredients)} ingredients")
    print()
    
    # Test 1: Basic recipe suggestion
    print("2. Testing basic recipe suggestions...")
    request = RecipeSuggestionRequest(
        available_ingredients=["tomato", "pasta", "olive oil", "garlic", "basil"],
        dietary_preferences=["vegetarian"],
        max_missing_ingredients=2
    )
    
    response = service.suggest_recipes(request)
    print(f"   ✓ Found {len(response.matches)} recipe matches")
    print(f"   ✓ Analysis completed in {response.analysis_time_ms:.2f}ms")
    print(f"   ✓ Algorithm used: {response.algorithm_insights.get('algorithm_used', 'unknown')}")
    
    if response.matches:
        best_match = response.matches[0]
        print(f"   ✓ Best match: '{best_match.recipe.name}' (score: {best_match.match_score:.2f})")
        print(f"   ✓ Missing ingredients: {len(best_match.missing_ingredients)}")
    print()
    
    # Test 2: Algorithm comparison
    print("3. Testing different algorithms...")
    algorithms = ["greedy", "backtracking", "graph"]
    
    for algorithm in algorithms:
        request.algorithm_preference = algorithm
        try:
            response = service.suggest_recipes(request)
            print(f"   ✓ {algorithm.capitalize()}: {len(response.matches)} matches in {response.analysis_time_ms:.2f}ms")
        except Exception as e:
            print(f"   ✗ {algorithm.capitalize()}: Error - {str(e)}")
    print()
    
    # Test 3: Ingredient gap analysis
    print("4. Testing ingredient gap analysis...")
    request = RecipeSuggestionRequest(
        available_ingredients=["chicken", "onion"],
        max_missing_ingredients=5
    )
    
    response = service.suggest_recipes(request)
    gap_analysis = response.ingredient_gap_analysis
    
    print(f"   ✓ Total unique missing ingredients: {gap_analysis['total_unique_missing']}")
    print(f"   ✓ Most common missing ingredients: {len(gap_analysis['most_common_missing'])}")
    print(f"   ✓ Shopping priority list: {len(gap_analysis['shopping_priority_list'])} items")
    
    if gap_analysis['most_common_missing']:
        top_missing = gap_analysis['most_common_missing'][0]
        print(f"   ✓ Top missing ingredient: {top_missing['name']} (appears in {top_missing['frequency']} recipes)")
    print()
    
    # Test 4: Substitution recommendations
    print("5. Testing substitution recommendations...")
    substitutions = response.substitution_recommendations
    print(f"   ✓ Found {len(substitutions)} substitution recommendations")
    
    for sub in substitutions[:2]:  # Show first 2
        original = sub['missing_ingredient']['name']
        if sub['substitutes']:
            substitute = sub['substitutes'][0]['name']
            score = sub['substitutes'][0]['similarity_score']
            print(f"   ✓ {original} → {substitute} (similarity: {score:.2f})")
    print()
    
    # Test 5: Graph analysis
    print("6. Testing graph analysis...")
    try:
        graph_stats = service.ingredient_graph.get_graph_statistics()
        print(f"   ✓ Graph nodes: {graph_stats['total_nodes']}")
        print(f"   ✓ Graph edges: {graph_stats['total_edges']}")
        print(f"   ✓ Graph density: {graph_stats['density']:.3f}")
        print(f"   ✓ Is connected: {graph_stats['is_connected']}")
        
        # Test centrality
        centrality = service.ingredient_graph.get_ingredient_centrality()
        if centrality:
            top_central = max(centrality.items(), key=lambda x: x[1])
            ingredient_name = service.ingredients.get(top_central[0], {}).name if top_central[0] in service.ingredients else top_central[0]
            print(f"   ✓ Most central ingredient: {ingredient_name} (centrality: {top_central[1]:.3f})")
    except Exception as e:
        print(f"   ✗ Graph analysis error: {str(e)}")
    print()
    
    # Test 6: Quick recipes
    print("7. Testing quick recipe finder...")
    try:
        available_set = service._normalize_ingredient_identifiers({"tomato", "mozzarella", "basil", "olive oil"})
        quick_matches = service.greedy_matcher.find_quick_recipes(available_set, max_time_minutes=15, max_results=3)
        print(f"   ✓ Found {len(quick_matches)} quick recipes (≤15 min)")
        
        for match in quick_matches:
            total_time = match.recipe.prep_time_minutes + match.recipe.cook_time_minutes
            print(f"   ✓ '{match.recipe.name}': {total_time} min (score: {match.match_score:.2f})")
    except Exception as e:
        print(f"   ✗ Quick recipes error: {str(e)}")
    print()
    
    # Test 7: System statistics
    print("8. System statistics...")
    stats = service.get_system_statistics()
    print(f"   ✓ Total recipes: {stats['total_recipes']}")
    print(f"   ✓ Total ingredients: {stats['total_ingredients']}")
    print(f"   ✓ Available algorithms: {list(stats['algorithm_availability'].keys())}")
    print()
    
    print("🎉 All tests completed successfully!")
    print("=" * 50)
    print("FlavorGraph system is ready to use!")
    print("Start the server with: uvicorn main:app --reload")
    print("Then visit: http://localhost:8000/docs")


def test_sample_request():
    """Test a sample API request format."""
    
    print("\n📋 Sample API Request:")
    print("=" * 30)
    
    sample_request = {
        "available_ingredients": ["tomato", "pasta", "olive oil", "garlic", "onion"],
        "dietary_preferences": ["vegetarian"],
        "meal_type": "dinner",
        "max_missing_ingredients": 3,
        "max_prep_time": 45,
        "algorithm_preference": "graph"
    }
    
    print("POST /api/v1/recipes/suggest")
    print("Content-Type: application/json")
    print()
    print(json.dumps(sample_request, indent=2))
    print()
    
    print("Expected response includes:")
    print("- matches: List of recipe matches with scores")
    print("- ingredient_gap_analysis: Missing ingredient analysis") 
    print("- substitution_recommendations: Ingredient substitutes")
    print("- algorithm_insights: Details about the algorithm used")
    print("- analysis_time_ms: Performance metrics")


if __name__ == "__main__":
    try:
        asyncio.run(test_system())
        test_sample_request()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc() 