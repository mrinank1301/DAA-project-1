from typing import List, Dict, Set, Tuple, Optional, Any
from models.recipe import Recipe, RecipeMatch, RecipeSuggestionRequest
from models.ingredient import Ingredient
import time
import logging

logger = logging.getLogger(__name__)


class BacktrackingRecipeMatcher:
    """
    Backtracking algorithm for finding optimal recipe matches.
    Explores all possible combinations to find the best matches.
    """
    
    def __init__(self, recipes: Dict[str, Recipe], ingredients: Dict[str, Ingredient]):
        self.recipes = recipes
        self.ingredients = ingredients
        self.best_matches = []
        self.exploration_count = 0
        self.max_explorations = 10000  # Limit to prevent infinite loops
        
    def find_optimal_recipes(self, request: RecipeSuggestionRequest, 
                           max_results: int = 10) -> List[RecipeMatch]:
        """
        Find optimal recipe matches using backtracking algorithm.
        """
        start_time = time.time()
        self.best_matches = []
        self.exploration_count = 0
        
        available_ingredients = set(request.available_ingredients)
        
        # Convert ingredient names to IDs if needed
        available_ingredient_ids = self._normalize_ingredient_identifiers(available_ingredients)
        
        # Filter recipes based on constraints
        candidate_recipes = self._filter_recipes_by_constraints(request)
        
        if not candidate_recipes:
            return []
        
        # Initialize backtracking search
        current_solution = []
        self._backtrack_search(
            candidate_recipes=list(candidate_recipes.keys()),
            available_ingredients=available_ingredient_ids,
            current_solution=current_solution,
            current_index=0,
            request=request,
            max_results=max_results
        )
        
        # Sort by match score and return top results
        self.best_matches.sort(key=lambda x: x.match_score, reverse=True)
        
        end_time = time.time()
        logger.info(f"Backtracking completed in {(end_time - start_time) * 1000:.2f}ms "
                   f"with {self.exploration_count} explorations")
        
        return self.best_matches[:max_results]
    
    def _backtrack_search(self, candidate_recipes: List[str], 
                         available_ingredients: Set[str],
                         current_solution: List[str],
                         current_index: int,
                         request: RecipeSuggestionRequest,
                         max_results: int):
        """
        Recursive backtracking search for optimal recipe combinations.
        """
        # Check exploration limit
        self.exploration_count += 1
        if self.exploration_count > self.max_explorations:
            return
        
        # Base case: we've found a solution
        if len(current_solution) >= max_results or current_index >= len(candidate_recipes):
            if current_solution:
                self._evaluate_solution(current_solution, available_ingredients, request)
            return
        
        # Early termination if we have enough good matches
        if len(self.best_matches) >= max_results * 2:  # Keep exploring for better solutions
            min_score = min(match.match_score for match in self.best_matches)
            if min_score > 0.8:  # High threshold for early termination
                return
        
        recipe_id = candidate_recipes[current_index]
        
        # Branch 1: Include this recipe
        if self._is_recipe_viable(recipe_id, available_ingredients, request):
            current_solution.append(recipe_id)
            self._backtrack_search(
                candidate_recipes, available_ingredients, 
                current_solution, current_index + 1, 
                request, max_results
            )
            current_solution.pop()  # Backtrack
        
        # Branch 2: Skip this recipe
        self._backtrack_search(
            candidate_recipes, available_ingredients,
            current_solution, current_index + 1,
            request, max_results
        )
    
    def _is_recipe_viable(self, recipe_id: str, available_ingredients: Set[str], 
                         request: RecipeSuggestionRequest) -> bool:
        """
        Check if a recipe is viable given constraints.
        """
        if recipe_id not in self.recipes:
            return False
            
        recipe = self.recipes[recipe_id]
        
        # Check dietary restrictions
        if request.dietary_preferences:
            if not self._check_dietary_compatibility(recipe, request.dietary_preferences):
                return False
        
        # Check excluded ingredients
        if request.exclude_ingredients:
            recipe_ingredient_ids = {ri.ingredient_id for ri in recipe.ingredients}
            if recipe_ingredient_ids.intersection(set(request.exclude_ingredients)):
                return False
        
        # Check missing ingredients constraint
        required_ingredients = {ri.ingredient_id for ri in recipe.ingredients if not ri.is_optional}
        missing_ingredients = required_ingredients - available_ingredients
        
        if len(missing_ingredients) > request.max_missing_ingredients:
            return False
        
        return True
    
    def _evaluate_solution(self, solution: List[str], available_ingredients: Set[str],
                          request: RecipeSuggestionRequest):
        """
        Evaluate a solution (set of recipes) and add to best matches if good enough.
        """
        for recipe_id in solution:
            if recipe_id in self.recipes:
                match = self._create_recipe_match(recipe_id, available_ingredients, request)
                if match and match.match_score > 0.1:  # Minimum threshold
                    # Check if we already have this recipe
                    existing_ids = {m.recipe.id for m in self.best_matches}
                    if recipe_id not in existing_ids:
                        self.best_matches.append(match)
    
    def _create_recipe_match(self, recipe_id: str, available_ingredients: Set[str],
                           request: RecipeSuggestionRequest) -> Optional[RecipeMatch]:
        """
        Create a RecipeMatch object with detailed analysis.
        """
        if recipe_id not in self.recipes:
            return None
            
        recipe = self.recipes[recipe_id]
        
        # Analyze ingredient matches
        required_ingredients = {ri.ingredient_id for ri in recipe.ingredients if not ri.is_optional}
        optional_ingredients = {ri.ingredient_id for ri in recipe.ingredients if ri.is_optional}
        all_recipe_ingredients = required_ingredients.union(optional_ingredients)
        
        # Direct matches
        direct_matches = available_ingredients.intersection(all_recipe_ingredients)
        direct_required_matches = available_ingredients.intersection(required_ingredients)
        
        # Missing ingredients
        missing_required = required_ingredients - available_ingredients
        missing_optional = optional_ingredients - available_ingredients
        
        # Calculate match score using backtracking-specific logic
        match_score = self._calculate_backtracking_score(
            recipe, direct_required_matches, required_ingredients,
            direct_matches, all_recipe_ingredients, request
        )
        
        # Find substitutable ingredients
        substitutable = self._find_substitutable_ingredients(missing_required, available_ingredients)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            match_score, len(missing_required), len(required_ingredients)
        )
        
        reasoning = self._generate_reasoning(
            len(direct_required_matches), len(required_ingredients),
            len(missing_required), len(substitutable)
        )
        
        return RecipeMatch(
            recipe=recipe,
            match_score=match_score,
            available_ingredients=list(direct_matches),
            missing_ingredients=list(missing_required),
            substitutable_ingredients=list(substitutable.keys()),
            confidence_score=confidence_score,
            algorithm_used="backtracking",
            reasoning=reasoning
        )
    
    def _calculate_backtracking_score(self, recipe: Recipe, direct_required_matches: Set[str],
                                    required_ingredients: Set[str], direct_matches: Set[str],
                                    all_recipe_ingredients: Set[str], 
                                    request: RecipeSuggestionRequest) -> float:
        """
        Calculate match score using backtracking-specific logic.
        """
        if not required_ingredients:
            return 1.0
        
        # Base score from required ingredient matches
        required_match_ratio = len(direct_required_matches) / len(required_ingredients)
        base_score = required_match_ratio
        
        # Bonus for optional ingredient matches
        optional_ingredients = all_recipe_ingredients - required_ingredients
        if optional_ingredients:
            optional_matches = direct_matches.intersection(optional_ingredients)
            optional_bonus = len(optional_matches) / len(optional_ingredients) * 0.15
            base_score += optional_bonus
        
        # Penalty for complexity mismatch
        if request.difficulty_level:
            if recipe.difficulty.value != request.difficulty_level.value:
                complexity_penalty = 0.1
                base_score -= complexity_penalty
        
        # Time constraint bonus/penalty
        if request.max_prep_time:
            if recipe.prep_time_minutes <= request.max_prep_time:
                base_score += 0.05  # Small bonus for meeting time constraint
            else:
                base_score -= 0.2   # Penalty for exceeding time limit
        
        if request.max_cook_time:
            if recipe.cook_time_minutes <= request.max_cook_time:
                base_score += 0.05
            else:
                base_score -= 0.2
        
        # Cuisine preference bonus
        if request.cuisine_preference and recipe.cuisine:
            if recipe.cuisine.lower() == request.cuisine_preference.lower():
                base_score += 0.1
        
        # Meal type bonus
        if request.meal_type and request.meal_type in recipe.meal_types:
            base_score += 0.1
        
        return min(1.0, max(0.0, base_score))
    
    def _find_substitutable_ingredients(self, missing_ingredients: Set[str], 
                                      available_ingredients: Set[str]) -> Dict[str, str]:
        """
        Find substitutable ingredients for missing ones.
        """
        substitutable = {}
        
        for missing_id in missing_ingredients:
            if missing_id in self.ingredients:
                missing_ingredient = self.ingredients[missing_id]
                
                # Check direct substitutes
                for substitute_id in missing_ingredient.common_substitutes:
                    if substitute_id in available_ingredients:
                        substitutable[missing_id] = substitute_id
                        break
                
                # If no direct substitute, look for category matches
                if missing_id not in substitutable:
                    for available_id in available_ingredients:
                        if available_id in self.ingredients:
                            available_ingredient = self.ingredients[available_id]
                            if (missing_ingredient.category == available_ingredient.category and
                                self._check_dietary_tags_compatibility(missing_ingredient, available_ingredient)):
                                substitutable[missing_id] = available_id
                                break
        
        return substitutable
    
    def _check_dietary_tags_compatibility(self, ingredient1: Ingredient, ingredient2: Ingredient) -> bool:
        """Check if two ingredients are compatible in terms of dietary tags."""
        # If one is more restrictive, it should be compatible with the less restrictive
        tags1 = set(ingredient1.dietary_tags)
        tags2 = set(ingredient2.dietary_tags)
        
        # If ingredient2 has all the dietary tags of ingredient1, it's compatible
        return tags1.issubset(tags2) or tags2.issubset(tags1)
    
    def _calculate_confidence_score(self, match_score: float, missing_count: int, 
                                  total_required: int) -> float:
        """Calculate confidence score for the match."""
        base_confidence = match_score
        
        # Reduce confidence based on missing ingredients
        if total_required > 0:
            missing_ratio = missing_count / total_required
            confidence_reduction = missing_ratio * 0.3
            base_confidence -= confidence_reduction
        
        # Boost confidence for perfect or near-perfect matches
        if match_score > 0.9:
            base_confidence = min(1.0, base_confidence + 0.1)
        
        return max(0.0, min(1.0, base_confidence))
    
    def _generate_reasoning(self, direct_matches: int, total_required: int,
                          missing_count: int, substitutable_count: int) -> str:
        """Generate human-readable reasoning for the match."""
        reasoning_parts = []
        
        if total_required > 0:
            match_percentage = (direct_matches / total_required) * 100
            reasoning_parts.append(f"{match_percentage:.1f}% ingredient match ({direct_matches}/{total_required})")
        
        if missing_count > 0:
            reasoning_parts.append(f"{missing_count} missing ingredients")
            
        if substitutable_count > 0:
            reasoning_parts.append(f"{substitutable_count} substitutable ingredients found")
        
        reasoning_parts.append("found through exhaustive backtracking search")
        
        return ", ".join(reasoning_parts)
    
    def _filter_recipes_by_constraints(self, request: RecipeSuggestionRequest) -> Dict[str, Recipe]:
        """Filter recipes based on hard constraints."""
        filtered_recipes = {}
        
        for recipe_id, recipe in self.recipes.items():
            # Check time constraints
            if request.max_prep_time and recipe.prep_time_minutes > request.max_prep_time:
                continue
                
            if request.max_cook_time and recipe.cook_time_minutes > request.max_cook_time:
                continue
            
            # Check difficulty level
            if request.difficulty_level and recipe.difficulty != request.difficulty_level:
                continue
            
            # Check meal type
            if request.meal_type and request.meal_type not in recipe.meal_types:
                continue
            
            # Check cuisine preference
            if request.cuisine_preference and recipe.cuisine:
                if recipe.cuisine.lower() != request.cuisine_preference.lower():
                    continue
            
            filtered_recipes[recipe_id] = recipe
        
        return filtered_recipes
    
    def _check_dietary_compatibility(self, recipe: Recipe, dietary_preferences: List[str]) -> bool:
        """Check if recipe is compatible with dietary preferences."""
        recipe_tags = set(tag.lower() for tag in recipe.dietary_tags)
        required_tags = set(pref.lower() for pref in dietary_preferences)
        
        # Recipe must have all required dietary tags
        return required_tags.issubset(recipe_tags)
    
    def _normalize_ingredient_identifiers(self, ingredient_names: Set[str]) -> Set[str]:
        """Convert ingredient names to IDs if needed."""
        normalized_ids = set()
        
        for name in ingredient_names:
            # If it's already an ID (exists in ingredients dict)
            if name in self.ingredients:
                normalized_ids.add(name)
            else:
                # Try to find by name or alias
                for ingredient_id, ingredient in self.ingredients.items():
                    if (ingredient.name.lower() == name.lower() or 
                        name.lower() in [alias.lower() for alias in ingredient.aliases]):
                        normalized_ids.add(ingredient_id)
                        break
        
        return normalized_ids
    
    def get_algorithm_insights(self) -> Dict[str, Any]:
        """Get insights about the backtracking algorithm performance."""
        return {
            "algorithm": "backtracking",
            "explorations_performed": self.exploration_count,
            "max_explorations_limit": self.max_explorations,
            "solutions_found": len(self.best_matches),
            "search_completeness": "exhaustive" if self.exploration_count < self.max_explorations else "limited",
            "optimization_approach": "global_optimal"
        } 