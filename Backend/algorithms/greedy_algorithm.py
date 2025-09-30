from typing import List, Dict, Set, Tuple, Optional, Any
from models.recipe import Recipe, RecipeMatch, RecipeSuggestionRequest
from models.ingredient import Ingredient
import time
import heapq
import logging

logger = logging.getLogger(__name__)


class GreedyRecipeMatcher:
    """
    Greedy algorithm for fast recipe recommendations.
    Makes locally optimal choices at each step for quick results.
    """
    
    def __init__(self, recipes: Dict[str, Recipe], ingredients: Dict[str, Ingredient]):
        self.recipes = recipes
        self.ingredients = ingredients
        
    def find_recipes_greedy(self, request: RecipeSuggestionRequest, 
                           max_results: int = 10) -> List[RecipeMatch]:
        """
        Find recipe matches using greedy algorithm for speed.
        """
        start_time = time.time()
        
        available_ingredients = set(request.available_ingredients)
        available_ingredient_ids = self._normalize_ingredient_identifiers(available_ingredients)
        
        # Quick scoring of all recipes
        recipe_scores = []
        
        for recipe_id, recipe in self.recipes.items():
            # Fast filtering
            if not self._quick_filter_recipe(recipe, request):
                continue
            
            # Calculate greedy score (fast heuristic)
            score = self._calculate_greedy_score(recipe, available_ingredient_ids, request)
            
            if score > 0.1:  # Minimum threshold
                heapq.heappush(recipe_scores, (-score, recipe_id))  # Use negative for max heap
        
        # Extract top candidates
        matches = []
        processed_count = 0
        
        while recipe_scores and len(matches) < max_results and processed_count < max_results * 2:
            neg_score, recipe_id = heapq.heappop(recipe_scores)
            score = -neg_score
            
            match = self._create_detailed_match(recipe_id, available_ingredient_ids, request, score)
            if match:
                matches.append(match)
            
            processed_count += 1
        
        end_time = time.time()
        logger.info(f"Greedy algorithm completed in {(end_time - start_time) * 1000:.2f}ms")
        
        return matches
    
    def _quick_filter_recipe(self, recipe: Recipe, request: RecipeSuggestionRequest) -> bool:
        """
        Quick filtering of recipes based on hard constraints.
        """
        # Time constraints
        if request.max_prep_time and recipe.prep_time_minutes > request.max_prep_time:
            return False
            
        if request.max_cook_time and recipe.cook_time_minutes > request.max_cook_time:
            return False
        
        # Difficulty level
        if request.difficulty_level and recipe.difficulty != request.difficulty_level:
            return False
        
        # Meal type
        if request.meal_type and request.meal_type not in recipe.meal_types:
            return False
        
        # Dietary preferences (quick check)
        if request.dietary_preferences:
            recipe_tags = set(tag.lower() for tag in recipe.dietary_tags)
            required_tags = set(pref.lower() for pref in request.dietary_preferences)
            if not required_tags.issubset(recipe_tags):
                return False
        
        # Excluded ingredients
        if request.exclude_ingredients:
            recipe_ingredient_ids = {ri.ingredient_id for ri in recipe.ingredients}
            if recipe_ingredient_ids.intersection(set(request.exclude_ingredients)):
                return False
        
        return True
    
    def _calculate_greedy_score(self, recipe: Recipe, available_ingredients: Set[str],
                              request: RecipeSuggestionRequest) -> float:
        """
        Calculate a fast greedy score for the recipe.
        """
        required_ingredients = {ri.ingredient_id for ri in recipe.ingredients if not ri.is_optional}
        optional_ingredients = {ri.ingredient_id for ri in recipe.ingredients if ri.is_optional}
        
        if not required_ingredients:
            return 1.0
        
        # Direct matches (greedy choice: prioritize direct matches)
        direct_required_matches = available_ingredients.intersection(required_ingredients)
        direct_optional_matches = available_ingredients.intersection(optional_ingredients)
        
        # Base score from required ingredients
        required_match_ratio = len(direct_required_matches) / len(required_ingredients)
        
        # Greedy heuristic: heavily weight direct matches
        base_score = required_match_ratio * required_match_ratio  # Quadratic bonus for direct matches
        
        # Quick bonus for optional ingredients
        if optional_ingredients:
            optional_bonus = len(direct_optional_matches) / len(optional_ingredients) * 0.1
            base_score += optional_bonus
        
        # Missing ingredients penalty (greedy: avoid recipes with many missing ingredients)
        missing_count = len(required_ingredients) - len(direct_required_matches)
        if missing_count > request.max_missing_ingredients:
            return 0.0  # Hard cutoff
        
        missing_penalty = missing_count / max(len(required_ingredients), 1) * 0.3
        base_score -= missing_penalty
        
        # Quick popularity boost
        if hasattr(recipe, 'popularity_score') and recipe.popularity_score > 0:
            base_score += min(recipe.popularity_score * 0.1, 0.2)
        
        # Rating boost
        if hasattr(recipe, 'average_rating') and recipe.average_rating:
            rating_boost = (recipe.average_rating / 5.0) * 0.15
            base_score += rating_boost
        
        # Cuisine preference
        if request.cuisine_preference and recipe.cuisine:
            if recipe.cuisine.lower() == request.cuisine_preference.lower():
                base_score += 0.15
        
        # Time preference (greedy: prefer faster recipes)
        total_time = recipe.prep_time_minutes + recipe.cook_time_minutes
        if total_time <= 30:  # Quick recipes
            base_score += 0.1
        elif total_time > 120:  # Long recipes
            base_score -= 0.1
        
        return min(1.0, max(0.0, base_score))
    
    def _create_detailed_match(self, recipe_id: str, available_ingredients: Set[str],
                             request: RecipeSuggestionRequest, initial_score: float) -> Optional[RecipeMatch]:
        """
        Create a detailed RecipeMatch with more thorough analysis.
        """
        if recipe_id not in self.recipes:
            return None
        
        recipe = self.recipes[recipe_id]
        
        # Detailed ingredient analysis
        required_ingredients = {ri.ingredient_id for ri in recipe.ingredients if not ri.is_optional}
        optional_ingredients = {ri.ingredient_id for ri in recipe.ingredients if ri.is_optional}
        all_recipe_ingredients = required_ingredients.union(optional_ingredients)
        
        # Matches and missing
        direct_matches = available_ingredients.intersection(all_recipe_ingredients)
        missing_required = required_ingredients - available_ingredients
        missing_optional = optional_ingredients - available_ingredients
        
        # Find substitutes using greedy approach
        substitutable = self._find_greedy_substitutes(missing_required, available_ingredients)
        
        # Refine score with detailed analysis
        refined_score = self._refine_score(
            initial_score, recipe, direct_matches, missing_required,
            substitutable, request
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(refined_score, len(missing_required), len(required_ingredients))
        
        # Generate reasoning
        reasoning = self._generate_greedy_reasoning(
            len(direct_matches & required_ingredients), len(required_ingredients),
            len(missing_required), len(substitutable), recipe
        )
        
        return RecipeMatch(
            recipe=recipe,
            match_score=refined_score,
            available_ingredients=list(direct_matches),
            missing_ingredients=list(missing_required),
            substitutable_ingredients=list(substitutable.keys()),
            confidence_score=confidence,
            algorithm_used="greedy",
            reasoning=reasoning
        )
    
    def _find_greedy_substitutes(self, missing_ingredients: Set[str], 
                               available_ingredients: Set[str]) -> Dict[str, str]:
        """
        Find substitutes using greedy approach (first suitable match).
        """
        substitutable = {}
        
        for missing_id in missing_ingredients:
            if missing_id not in self.ingredients:
                continue
                
            missing_ingredient = self.ingredients[missing_id]
            
            # Greedy choice 1: Direct substitutes (first match wins)
            for substitute_id in missing_ingredient.common_substitutes:
                if substitute_id in available_ingredients:
                    substitutable[missing_id] = substitute_id
                    break
            
            # Greedy choice 2: Same category (first match wins)
            if missing_id not in substitutable:
                for available_id in available_ingredients:
                    if available_id in self.ingredients:
                        available_ingredient = self.ingredients[available_id]
                        if missing_ingredient.category == available_ingredient.category:
                            # Quick dietary compatibility check
                            if self._quick_dietary_check(missing_ingredient, available_ingredient):
                                substitutable[missing_id] = available_id
                                break
        
        return substitutable
    
    def _quick_dietary_check(self, ingredient1: Ingredient, ingredient2: Ingredient) -> bool:
        """Quick dietary compatibility check."""
        tags1 = set(ingredient1.dietary_tags)
        tags2 = set(ingredient2.dietary_tags)
        
        # Simple check: if one has more restrictive tags, it should include the other's tags
        return len(tags1.intersection(tags2)) > 0 or (not tags1 and not tags2)
    
    def _refine_score(self, initial_score: float, recipe: Recipe, direct_matches: Set[str],
                     missing_required: Set[str], substitutable: Dict[str, str],
                     request: RecipeSuggestionRequest) -> float:
        """
        Refine the initial greedy score with additional factors.
        """
        refined_score = initial_score
        
        # Substitute bonus
        if substitutable:
            substitute_bonus = len(substitutable) / max(len(missing_required), 1) * 0.2
            refined_score += substitute_bonus
        
        # Complexity matching
        if hasattr(recipe, 'ingredient_complexity_score') and recipe.ingredient_complexity_score:
            # Prefer simpler recipes when many ingredients are missing
            if len(missing_required) > 2 and recipe.ingredient_complexity_score > 0.7:
                refined_score -= 0.1
        
        # Equipment availability (assume basic equipment available)
        if recipe.equipment_needed:
            basic_equipment = {'oven', 'stove', 'pan', 'pot', 'knife', 'cutting board'}
            advanced_equipment = set(recipe.equipment_needed) - basic_equipment
            if advanced_equipment:
                refined_score -= len(advanced_equipment) * 0.05  # Small penalty
        
        # Seasonal bonus (if available)
        # This would require current season information
        
        return min(1.0, max(0.0, refined_score))
    
    def _calculate_confidence(self, score: float, missing_count: int, total_required: int) -> float:
        """Calculate confidence score for greedy match."""
        base_confidence = score
        
        # Confidence decreases with missing ingredients
        if total_required > 0:
            missing_ratio = missing_count / total_required
            confidence_reduction = missing_ratio * 0.25
            base_confidence -= confidence_reduction
        
        # High scores get confidence boost
        if score > 0.8:
            base_confidence = min(1.0, base_confidence + 0.1)
        
        # Greedy algorithm is less confident than exhaustive search
        base_confidence *= 0.95
        
        return max(0.0, min(1.0, base_confidence))
    
    def _generate_greedy_reasoning(self, direct_matches: int, total_required: int,
                                 missing_count: int, substitutable_count: int,
                                 recipe: Recipe) -> str:
        """Generate reasoning for greedy match."""
        reasoning_parts = []
        
        if total_required > 0:
            match_percentage = (direct_matches / total_required) * 100
            reasoning_parts.append(f"{match_percentage:.1f}% direct ingredient match")
        
        if missing_count > 0:
            reasoning_parts.append(f"{missing_count} missing ingredients")
        
        if substitutable_count > 0:
            reasoning_parts.append(f"{substitutable_count} substitutes available")
        
        # Add recipe characteristics
        if recipe.difficulty:
            reasoning_parts.append(f"{recipe.difficulty.value} difficulty")
        
        total_time = recipe.prep_time_minutes + recipe.cook_time_minutes
        reasoning_parts.append(f"{total_time} minutes total time")
        
        reasoning_parts.append("selected by greedy algorithm for speed")
        
        return ", ".join(reasoning_parts)
    
    def _normalize_ingredient_identifiers(self, ingredient_names: Set[str]) -> Set[str]:
        """Convert ingredient names to IDs if needed."""
        normalized_ids = set()
        
        for name in ingredient_names:
            # If it's already an ID
            if name in self.ingredients:
                normalized_ids.add(name)
            else:
                # Find by name or alias (greedy: first match)
                for ingredient_id, ingredient in self.ingredients.items():
                    if (ingredient.name.lower() == name.lower() or 
                        name.lower() in [alias.lower() for alias in ingredient.aliases]):
                        normalized_ids.add(ingredient_id)
                        break
        
        return normalized_ids
    
    def get_algorithm_insights(self) -> Dict[str, Any]:
        """Get insights about the greedy algorithm."""
        return {
            "algorithm": "greedy",
            "optimization_approach": "local_optimal",
            "speed_priority": "high",
            "completeness": "heuristic",
            "best_use_case": "real_time_recommendations",
            "trade_offs": "speed_vs_optimality"
        }
    
    def find_recipes_by_popularity(self, available_ingredients: Set[str], 
                                 max_results: int = 5) -> List[RecipeMatch]:
        """
        Greedy approach: find most popular recipes that can be made.
        """
        available_ingredient_ids = self._normalize_ingredient_identifiers(available_ingredients)
        
        # Sort recipes by popularity (greedy choice)
        sorted_recipes = sorted(
            self.recipes.items(),
            key=lambda x: getattr(x[1], 'popularity_score', 0),
            reverse=True
        )
        
        matches = []
        for recipe_id, recipe in sorted_recipes:
            if len(matches) >= max_results:
                break
                
            required_ingredients = {ri.ingredient_id for ri in recipe.ingredients if not ri.is_optional}
            missing = required_ingredients - available_ingredient_ids
            
            # Greedy: take first recipes that can be made with few missing ingredients
            if len(missing) <= 3:  # Arbitrary threshold
                score = 1.0 - (len(missing) / max(len(required_ingredients), 1)) * 0.5
                
                match = RecipeMatch(
                    recipe=recipe,
                    match_score=score,
                    available_ingredients=list(available_ingredient_ids.intersection(required_ingredients)),
                    missing_ingredients=list(missing),
                    substitutable_ingredients=[],
                    confidence_score=score * 0.9,
                    algorithm_used="greedy_popularity",
                    reasoning=f"Popular recipe with {len(missing)} missing ingredients"
                )
                matches.append(match)
        
        return matches
    
    def find_quick_recipes(self, available_ingredients: Set[str], 
                          max_time_minutes: int = 30, 
                          max_results: int = 5) -> List[RecipeMatch]:
        """
        Greedy approach: find quickest recipes that can be made.
        """
        available_ingredient_ids = self._normalize_ingredient_identifiers(available_ingredients)
        
        # Filter and sort by time (greedy choice)
        quick_recipes = [
            (recipe_id, recipe) for recipe_id, recipe in self.recipes.items()
            if (recipe.prep_time_minutes + recipe.cook_time_minutes) <= max_time_minutes
        ]
        
        quick_recipes.sort(key=lambda x: x[1].prep_time_minutes + x[1].cook_time_minutes)
        
        matches = []
        for recipe_id, recipe in quick_recipes:
            if len(matches) >= max_results:
                break
                
            required_ingredients = {ri.ingredient_id for ri in recipe.ingredients if not ri.is_optional}
            missing = required_ingredients - available_ingredient_ids
            
            if len(missing) <= 2:  # Quick recipes should have few missing ingredients
                total_time = recipe.prep_time_minutes + recipe.cook_time_minutes
                time_score = 1.0 - (total_time / max_time_minutes) * 0.3
                ingredient_score = 1.0 - (len(missing) / max(len(required_ingredients), 1)) * 0.4
                
                combined_score = (time_score + ingredient_score) / 2
                
                match = RecipeMatch(
                    recipe=recipe,
                    match_score=combined_score,
                    available_ingredients=list(available_ingredient_ids.intersection(required_ingredients)),
                    missing_ingredients=list(missing),
                    substitutable_ingredients=[],
                    confidence_score=combined_score * 0.85,
                    algorithm_used="greedy_time",
                    reasoning=f"Quick recipe ({total_time} min) with {len(missing)} missing ingredients"
                )
                matches.append(match)
        
        return matches 