from typing import List, Dict, Any, Set, Optional
import re
import unicodedata
from datetime import datetime, timedelta


def normalize_ingredient_name(name: str) -> str:
    """
    Normalize ingredient name for consistent matching.
    """
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower().strip()
    
    # Remove accents and special characters
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))
    
    # Replace common variations
    replacements = {
        'fresh ': '',
        'dried ': '',
        'ground ': '',
        'chopped ': '',
        'diced ': '',
        'minced ': '',
        'sliced ': '',
        'whole ': '',
        'organic ': '',
        'extra virgin ': '',
        'sea salt': 'salt',
        'kosher salt': 'salt',
        'table salt': 'salt',
        'olive oil': 'olive_oil',
        'vegetable oil': 'oil',
        'cooking oil': 'oil'
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    # Remove extra spaces and replace spaces with underscores
    name = re.sub(r'\s+', '_', name.strip())
    
    # Remove special characters except underscores
    name = re.sub(r'[^a-z0-9_]', '', name)
    
    return name


def calculate_recipe_complexity(recipe_ingredient_count: int, 
                              instruction_count: int,
                              cooking_methods: List[str],
                              equipment_needed: List[str]) -> float:
    """
    Calculate a complexity score for a recipe based on various factors.
    Returns a score between 0.0 and 1.0.
    """
    # Base complexity from ingredient count
    ingredient_complexity = min(recipe_ingredient_count / 20.0, 1.0)  # Max at 20 ingredients
    
    # Instruction complexity
    instruction_complexity = min(instruction_count / 15.0, 1.0)  # Max at 15 steps
    
    # Cooking method complexity
    method_weights = {
        'raw': 0.1,
        'boiling': 0.2,
        'steaming': 0.3,
        'sauteing': 0.4,
        'frying': 0.5,
        'roasting': 0.6,
        'baking': 0.6,
        'grilling': 0.7,
        'braising': 0.8,
        'slow_cooking': 0.5
    }
    
    method_complexity = 0.0
    if cooking_methods:
        method_scores = [method_weights.get(method.lower(), 0.5) for method in cooking_methods]
        method_complexity = sum(method_scores) / len(method_scores)
    
    # Equipment complexity
    equipment_complexity = min(len(equipment_needed) / 10.0, 1.0)  # Max at 10 pieces
    
    # Weighted average
    total_complexity = (
        ingredient_complexity * 0.3 +
        instruction_complexity * 0.3 +
        method_complexity * 0.25 +
        equipment_complexity * 0.15
    )
    
    return min(max(total_complexity, 0.0), 1.0)


def format_cooking_time(minutes: int) -> str:
    """
    Format cooking time in a human-readable format.
    """
    if minutes < 60:
        return f"{minutes} minutes"
    elif minutes < 120:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours > 1 else ''} {remaining_minutes} minutes"
    else:
        hours = minutes // 60
        return f"{hours} hours"


def calculate_nutritional_density(nutritional_info: Dict[str, float]) -> float:
    """
    Calculate nutritional density score based on nutrient content.
    Higher score indicates more nutritionally dense.
    """
    if not nutritional_info:
        return 0.0
    
    # Weight different nutrients
    weights = {
        'protein_g': 4.0,      # High weight for protein
        'fiber_g': 3.0,        # High weight for fiber
        'fat_g': 1.0,          # Moderate weight for fat
        'carbs_g': 0.5,        # Lower weight for carbs
        'sugar_g': -1.0,       # Negative weight for sugar
        'sodium_mg': -0.001    # Negative weight for sodium (per mg)
    }
    
    score = 0.0
    calories = nutritional_info.get('calories_per_100g', 100)
    
    for nutrient, amount in nutritional_info.items():
        if nutrient in weights and amount is not None:
            # Normalize by calories to get density
            density_contribution = (amount / calories) * weights[nutrient] * 100
            score += density_contribution
    
    # Normalize to 0-1 range
    return max(0.0, min(1.0, (score + 10) / 20))


def extract_dietary_restrictions(tags: List[str]) -> Dict[str, bool]:
    """
    Extract dietary restriction information from tags.
    """
    dietary_map = {
        'vegetarian': False,
        'vegan': False,
        'gluten_free': False,
        'dairy_free': False,
        'nut_free': False,
        'keto': False,
        'paleo': False,
        'low_carb': False,
        'high_protein': False,
        'low_sodium': False
    }
    
    tag_mappings = {
        'vegetarian': 'vegetarian',
        'vegan': 'vegan',
        'gluten-free': 'gluten_free',
        'gluten free': 'gluten_free',
        'dairy-free': 'dairy_free',
        'dairy free': 'dairy_free',
        'nut-free': 'nut_free',
        'nut free': 'nut_free',
        'keto': 'keto',
        'ketogenic': 'keto',
        'paleo': 'paleo',
        'low-carb': 'low_carb',
        'low carb': 'low_carb',
        'high-protein': 'high_protein',
        'high protein': 'high_protein',
        'low-sodium': 'low_sodium',
        'low sodium': 'low_sodium'
    }
    
    for tag in tags:
        tag_lower = tag.lower().strip()
        if tag_lower in tag_mappings:
            dietary_map[tag_mappings[tag_lower]] = True
    
    return dietary_map


def generate_shopping_list(missing_ingredients: List[Dict[str, Any]], 
                          priority_threshold: float = 0.5) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate a categorized shopping list from missing ingredients.
    """
    shopping_list = {
        'high_priority': [],
        'medium_priority': [],
        'low_priority': [],
        'by_category': {}
    }
    
    for ingredient in missing_ingredients:
        priority_score = ingredient.get('priority_score', 0.0)
        category = ingredient.get('category', 'other')
        
        # Add to priority lists
        if priority_score >= 0.8:
            shopping_list['high_priority'].append(ingredient)
        elif priority_score >= priority_threshold:
            shopping_list['medium_priority'].append(ingredient)
        else:
            shopping_list['low_priority'].append(ingredient)
        
        # Add to category lists
        if category not in shopping_list['by_category']:
            shopping_list['by_category'][category] = []
        shopping_list['by_category'][category].append(ingredient)
    
    return shopping_list


def calculate_seasonal_score(ingredient_seasons: List[str], current_month: Optional[int] = None) -> float:
    """
    Calculate seasonal availability score for an ingredient.
    """
    if not ingredient_seasons:
        return 1.0  # Available year-round
    
    if current_month is None:
        current_month = datetime.now().month
    
    # Map months to seasons
    season_months = {
        'spring': [3, 4, 5],
        'summer': [6, 7, 8],
        'fall': [9, 10, 11],
        'autumn': [9, 10, 11],  # Alternative name for fall
        'winter': [12, 1, 2]
    }
    
    current_season = None
    for season, months in season_months.items():
        if current_month in months:
            current_season = season
            break
    
    if current_season and current_season in ingredient_seasons:
        return 1.0  # In season
    elif any(season in ingredient_seasons for season in season_months.keys()):
        return 0.5  # Out of season but seasonal
    else:
        return 1.0  # Year-round availability


def estimate_recipe_cost(ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Estimate recipe cost based on ingredient cost levels.
    """
    if not ingredients:
        return {'total_cost_level': 1, 'cost_category': 'budget', 'cost_breakdown': {}}
    
    cost_levels = []
    cost_breakdown = {'budget': 0, 'moderate': 0, 'expensive': 0, 'premium': 0}
    
    for ingredient in ingredients:
        cost_level = ingredient.get('cost_level', 2)  # Default to moderate
        cost_levels.append(cost_level)
        
        if cost_level <= 2:
            cost_breakdown['budget'] += 1
        elif cost_level == 3:
            cost_breakdown['moderate'] += 1
        elif cost_level == 4:
            cost_breakdown['expensive'] += 1
        else:
            cost_breakdown['premium'] += 1
    
    average_cost = sum(cost_levels) / len(cost_levels)
    
    if average_cost <= 2:
        cost_category = 'budget'
    elif average_cost <= 3:
        cost_category = 'moderate'
    elif average_cost <= 4:
        cost_category = 'expensive'
    else:
        cost_category = 'premium'
    
    return {
        'total_cost_level': round(average_cost, 1),
        'cost_category': cost_category,
        'cost_breakdown': cost_breakdown,
        'ingredient_count': len(ingredients)
    }


def validate_recipe_data(recipe_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate recipe data and return validation errors.
    """
    errors = {
        'required_fields': [],
        'invalid_values': [],
        'warnings': []
    }
    
    # Required fields
    required_fields = ['name', 'ingredients', 'instructions', 'prep_time_minutes', 'cook_time_minutes']
    for field in required_fields:
        if field not in recipe_data or not recipe_data[field]:
            errors['required_fields'].append(f"Missing required field: {field}")
    
    # Validate time values
    if 'prep_time_minutes' in recipe_data:
        prep_time = recipe_data['prep_time_minutes']
        if not isinstance(prep_time, int) or prep_time < 0:
            errors['invalid_values'].append("prep_time_minutes must be a non-negative integer")
    
    if 'cook_time_minutes' in recipe_data:
        cook_time = recipe_data['cook_time_minutes']
        if not isinstance(cook_time, int) or cook_time < 0:
            errors['invalid_values'].append("cook_time_minutes must be a non-negative integer")
    
    # Validate servings
    if 'servings' in recipe_data:
        servings = recipe_data['servings']
        if not isinstance(servings, int) or servings <= 0:
            errors['invalid_values'].append("servings must be a positive integer")
    
    # Validate ingredients
    if 'ingredients' in recipe_data:
        ingredients = recipe_data['ingredients']
        if not isinstance(ingredients, list) or len(ingredients) == 0:
            errors['invalid_values'].append("ingredients must be a non-empty list")
        else:
            for i, ingredient in enumerate(ingredients):
                if not isinstance(ingredient, dict):
                    errors['invalid_values'].append(f"ingredient {i} must be a dictionary")
                else:
                    required_ing_fields = ['ingredient_id', 'quantity', 'unit']
                    for field in required_ing_fields:
                        if field not in ingredient:
                            errors['invalid_values'].append(f"ingredient {i} missing {field}")
    
    # Validate instructions
    if 'instructions' in recipe_data:
        instructions = recipe_data['instructions']
        if not isinstance(instructions, list) or len(instructions) == 0:
            errors['invalid_values'].append("instructions must be a non-empty list")
    
    # Warnings for missing optional but recommended fields
    recommended_fields = ['description', 'cuisine', 'difficulty', 'tags']
    for field in recommended_fields:
        if field not in recipe_data or not recipe_data[field]:
            errors['warnings'].append(f"Recommended field missing: {field}")
    
    return errors


def format_ingredient_quantity(quantity: float, unit: str) -> str:
    """
    Format ingredient quantity in a human-readable way.
    """
    # Handle fractional quantities
    if quantity == int(quantity):
        quantity_str = str(int(quantity))
    elif quantity == 0.5:
        quantity_str = "1/2"
    elif quantity == 0.25:
        quantity_str = "1/4"
    elif quantity == 0.75:
        quantity_str = "3/4"
    elif quantity == 0.33:
        quantity_str = "1/3"
    elif quantity == 0.67:
        quantity_str = "2/3"
    else:
        quantity_str = f"{quantity:.1f}".rstrip('0').rstrip('.')
    
    # Handle unit pluralization
    if quantity > 1 and not unit.endswith('s') and unit not in ['tsp', 'tbsp', 'ml', 'g', 'kg', 'oz', 'lb']:
        if unit.endswith('y'):
            unit = unit[:-1] + 'ies'
        else:
            unit += 's'
    
    return f"{quantity_str} {unit}"


def calculate_prep_efficiency_score(prep_time: int, cook_time: int, 
                                  ingredient_count: int, instruction_count: int) -> float:
    """
    Calculate how efficient a recipe is in terms of prep time vs. complexity.
    Higher score means more efficient (less prep time for the complexity).
    """
    if prep_time <= 0:
        return 1.0
    
    # Calculate complexity factors
    complexity_score = (ingredient_count * 0.5 + instruction_count * 0.3) / 10
    time_efficiency = 60 / max(prep_time, 1)  # Inverse relationship with prep time
    
    # Combine factors
    efficiency = (time_efficiency + (1 / max(complexity_score, 0.1))) / 2
    
    return min(max(efficiency / 10, 0.0), 1.0)  # Normalize to 0-1 