from typing import List, Dict, Set, Optional, Any, Tuple
import time
import logging
from collections import defaultdict, Counter

from models.recipe import (
    Recipe, RecipeMatch, RecipeSuggestionRequest, RecipeSuggestionResponse
)
from models.ingredient import Ingredient, IngredientSubstitution
from algorithms.graph_algorithm import IngredientGraph
from algorithms.backtracking_algorithm import BacktrackingRecipeMatcher
from algorithms.greedy_algorithm import GreedyRecipeMatcher

logger = logging.getLogger(__name__)


class RecipeRecommendationService:
    """
    Main service for recipe recommendations that orchestrates all algorithms
    and provides comprehensive ingredient analysis.
    """
    
    def __init__(self):
        self.recipes: Dict[str, Recipe] = {}
        self.ingredients: Dict[str, Ingredient] = {}
        self.ingredient_graph = IngredientGraph()
        self.backtracking_matcher = None
        self.greedy_matcher = None
        self._initialize_matchers()
    
    def _initialize_matchers(self):
        """Initialize algorithm matchers."""
        self.backtracking_matcher = BacktrackingRecipeMatcher(self.recipes, self.ingredients)
        self.greedy_matcher = GreedyRecipeMatcher(self.recipes, self.ingredients)
    
    def add_recipe(self, recipe: Recipe):
        """Add a recipe to the system."""
        self.recipes[recipe.id] = recipe
        self.ingredient_graph.add_recipe(recipe)
        self._reinitialize_matchers()
    
    def add_ingredient(self, ingredient: Ingredient):
        """Add an ingredient to the system."""
        self.ingredients[ingredient.id] = ingredient
        self.ingredient_graph.add_ingredient(ingredient)
        self._reinitialize_matchers()
    
    def _reinitialize_matchers(self):
        """Reinitialize matchers when data changes."""
        self.backtracking_matcher = BacktrackingRecipeMatcher(self.recipes, self.ingredients)
        self.greedy_matcher = GreedyRecipeMatcher(self.recipes, self.ingredients)
    
    def suggest_recipes(self, request: RecipeSuggestionRequest) -> RecipeSuggestionResponse:
        """
        Main method to suggest recipes using the specified or optimal algorithm.
        """
        start_time = time.time()
        
        # Determine which algorithm to use
        algorithm = self._select_algorithm(request)
        
        # Get recipe matches
        matches = self._get_recipe_matches(request, algorithm)
        
        # Perform ingredient gap analysis
        ingredient_analysis = self._analyze_ingredient_gaps(request, matches)
        
        # Get substitution recommendations
        substitution_recommendations = self._get_substitution_recommendations(request, matches)
        
        # Get algorithm insights
        algorithm_insights = self._get_algorithm_insights(algorithm, request)
        
        end_time = time.time()
        analysis_time_ms = (end_time - start_time) * 1000
        
        return RecipeSuggestionResponse(
            matches=matches,
            total_recipes_analyzed=len(self.recipes),
            analysis_time_ms=analysis_time_ms,
            algorithm_insights=algorithm_insights,
            ingredient_gap_analysis=ingredient_analysis,
            substitution_recommendations=substitution_recommendations
        )
    
    def _select_algorithm(self, request: RecipeSuggestionRequest) -> str:
        """
        Select the optimal algorithm based on request characteristics.
        """
        if request.algorithm_preference:
            return request.algorithm_preference
        
        # Auto-select based on request characteristics
        num_recipes = len(self.recipes)
        num_available_ingredients = len(request.available_ingredients)
        
        # Use greedy for large datasets or when speed is important
        if num_recipes > 1000 or num_available_ingredients > 20:
            return "greedy"
        
        # Use backtracking for small datasets when accuracy is important
        if num_recipes < 100 and num_available_ingredients < 10:
            return "backtracking"
        
        # Use graph for medium datasets and when relationships matter
        return "graph"
    
    def _get_recipe_matches(self, request: RecipeSuggestionRequest, algorithm: str) -> List[RecipeMatch]:
        """Get recipe matches using the specified algorithm."""
        max_results = 10  # Default max results
        
        try:
            if algorithm == "greedy":
                return self.greedy_matcher.find_recipes_greedy(request, max_results)
            elif algorithm == "backtracking":
                return self.backtracking_matcher.find_optimal_recipes(request, max_results)
            elif algorithm == "graph":
                available_ingredients = self._normalize_ingredient_identifiers(set(request.available_ingredients))
                return self.ingredient_graph.recommend_recipes_graph(available_ingredients, max_results)
            else:
                logger.warning(f"Unknown algorithm: {algorithm}, falling back to greedy")
                return self.greedy_matcher.find_recipes_greedy(request, max_results)
        except Exception as e:
            logger.error(f"Error in algorithm {algorithm}: {str(e)}")
            # Fallback to greedy algorithm
            return self.greedy_matcher.find_recipes_greedy(request, max_results)
    
    def _analyze_ingredient_gaps(self, request: RecipeSuggestionRequest, 
                               matches: List[RecipeMatch]) -> Dict[str, Any]:
        """
        Analyze ingredient gaps across all suggested recipes.
        """
        available_ingredients = set(self._normalize_ingredient_identifiers(set(request.available_ingredients)))
        
        # Collect all missing ingredients across matches
        all_missing = []
        recipe_missing_map = {}
        
        for match in matches:
            missing = set(match.missing_ingredients)
            all_missing.extend(missing)
            recipe_missing_map[match.recipe.id] = missing
        
        # Count frequency of missing ingredients
        missing_frequency = Counter(all_missing)
        
        # Categorize missing ingredients
        missing_by_category = defaultdict(list)
        essential_missing = []  # Ingredients that appear in many recipes
        
        for ingredient_id, frequency in missing_frequency.items():
            if ingredient_id in self.ingredients:
                ingredient = self.ingredients[ingredient_id]
                missing_by_category[ingredient.category.value].append({
                    'id': ingredient_id,
                    'name': ingredient.name,
                    'frequency': frequency,
                    'cost_level': getattr(ingredient, 'cost_level', None)
                })
                
                # Essential if appears in >50% of suggested recipes
                if frequency > len(matches) * 0.5:
                    essential_missing.append({
                        'id': ingredient_id,
                        'name': ingredient.name,
                        'frequency': frequency,
                        'impact_score': frequency / len(matches)
                    })
        
        # Calculate shopping list priority
        shopping_priority = self._calculate_shopping_priority(missing_frequency, matches)
        
        # Analyze ingredient coverage
        coverage_analysis = self._analyze_ingredient_coverage(available_ingredients, matches)
        
        return {
            'total_unique_missing': len(missing_frequency),
            'most_common_missing': [
                {'ingredient_id': ing_id, 'frequency': freq, 'name': self.ingredients.get(ing_id, {}).name if ing_id in self.ingredients else ing_id}
                for ing_id, freq in missing_frequency.most_common(10)
            ],
            'missing_by_category': dict(missing_by_category),
            'essential_missing_ingredients': essential_missing,
            'shopping_priority_list': shopping_priority,
            'coverage_analysis': coverage_analysis,
            'recommendation': self._generate_gap_recommendations(missing_frequency, available_ingredients)
        }
    
    def _calculate_shopping_priority(self, missing_frequency: Counter, 
                                   matches: List[RecipeMatch]) -> List[Dict[str, Any]]:
        """
        Calculate shopping priority based on ingredient impact.
        """
        priority_list = []
        
        for ingredient_id, frequency in missing_frequency.items():
            if ingredient_id not in self.ingredients:
                continue
                
            ingredient = self.ingredients[ingredient_id]
            
            # Calculate impact score
            frequency_score = frequency / len(matches)
            
            # Cost consideration (lower cost = higher priority)
            cost_score = 1.0
            if hasattr(ingredient, 'cost_level') and ingredient.cost_level:
                cost_score = (6 - ingredient.cost_level) / 5  # Invert cost (1=expensive, 5=cheap)
            
            # Versatility score (how many different categories of recipes it enables)
            versatility_score = self._calculate_ingredient_versatility(ingredient_id, matches)
            
            # Combined priority score
            priority_score = (frequency_score * 0.4 + cost_score * 0.3 + versatility_score * 0.3)
            
            priority_list.append({
                'ingredient_id': ingredient_id,
                'name': ingredient.name,
                'priority_score': priority_score,
                'frequency': frequency,
                'estimated_cost_level': getattr(ingredient, 'cost_level', None),
                'category': ingredient.category.value,
                'impact_description': self._describe_ingredient_impact(ingredient_id, frequency, matches)
            })
        
        # Sort by priority score
        priority_list.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priority_list[:15]  # Top 15 priority ingredients
    
    def _calculate_ingredient_versatility(self, ingredient_id: str, matches: List[RecipeMatch]) -> float:
        """Calculate how versatile an ingredient is across different recipe types."""
        if ingredient_id not in self.ingredients:
            return 0.0
        
        recipe_categories = set()
        recipe_cuisines = set()
        
        for match in matches:
            if ingredient_id in match.missing_ingredients:
                recipe = match.recipe
                recipe_categories.update([mt.value for mt in recipe.meal_types])
                if recipe.cuisine:
                    recipe_cuisines.add(recipe.cuisine)
        
        # Versatility based on variety of meal types and cuisines
        category_variety = len(recipe_categories) / max(len(set(mt.value for match in matches for mt in match.recipe.meal_types)), 1)
        cuisine_variety = len(recipe_cuisines) / max(len(set(match.recipe.cuisine for match in matches if match.recipe.cuisine)), 1)
        
        return (category_variety + cuisine_variety) / 2
    
    def _describe_ingredient_impact(self, ingredient_id: str, frequency: int, 
                                  matches: List[RecipeMatch]) -> str:
        """Generate a description of what buying this ingredient would enable."""
        if frequency == 1:
            return f"Enables 1 additional recipe option"
        else:
            percentage = (frequency / len(matches)) * 100
            return f"Enables {frequency} additional recipes ({percentage:.1f}% of suggestions)"
    
    def _analyze_ingredient_coverage(self, available_ingredients: Set[str], 
                                   matches: List[RecipeMatch]) -> Dict[str, Any]:
        """Analyze how well available ingredients cover the suggested recipes."""
        if not matches:
            return {}
        
        total_recipes = len(matches)
        fully_covered = sum(1 for match in matches if not match.missing_ingredients)
        partially_covered = sum(1 for match in matches if match.missing_ingredients and len(match.missing_ingredients) <= 3)
        
        # Calculate average coverage
        coverage_scores = []
        for match in matches:
            recipe_ingredients = {ri.ingredient_id for ri in match.recipe.ingredients if not ri.is_optional}
            if recipe_ingredients:
                coverage = len(available_ingredients.intersection(recipe_ingredients)) / len(recipe_ingredients)
                coverage_scores.append(coverage)
        
        average_coverage = sum(coverage_scores) / len(coverage_scores) if coverage_scores else 0
        
        return {
            'total_suggested_recipes': total_recipes,
            'fully_covered_recipes': fully_covered,
            'partially_covered_recipes': partially_covered,
            'average_coverage_percentage': average_coverage * 100,
            'coverage_distribution': {
                'excellent_coverage': sum(1 for score in coverage_scores if score >= 0.9),
                'good_coverage': sum(1 for score in coverage_scores if 0.7 <= score < 0.9),
                'moderate_coverage': sum(1 for score in coverage_scores if 0.5 <= score < 0.7),
                'poor_coverage': sum(1 for score in coverage_scores if score < 0.5)
            }
        }
    
    def _generate_gap_recommendations(self, missing_frequency: Counter, 
                                    available_ingredients: Set[str]) -> List[str]:
        """Generate actionable recommendations for ingredient gaps."""
        recommendations = []
        
        if not missing_frequency:
            recommendations.append("Great! You have excellent ingredient coverage for the suggested recipes.")
            return recommendations
        
        most_common = missing_frequency.most_common(3)
        
        if len(most_common) > 0:
            top_missing = most_common[0]
            if top_missing[1] > 1:
                ingredient_name = self.ingredients.get(top_missing[0], {}).name if top_missing[0] in self.ingredients else top_missing[0]
                recommendations.append(f"Consider buying {ingredient_name} - it would unlock {top_missing[1]} additional recipe options.")
        
        # Category-based recommendations
        category_gaps = defaultdict(int)
        for ingredient_id in missing_frequency.keys():
            if ingredient_id in self.ingredients:
                category_gaps[self.ingredients[ingredient_id].category.value] += 1
        
        if category_gaps:
            top_category = max(category_gaps.items(), key=lambda x: x[1])
            recommendations.append(f"You're missing several {top_category[0]} ingredients. Focus on this category for maximum recipe variety.")
        
        # Staples recommendation
        basic_staples = {'salt', 'pepper', 'olive_oil', 'onion', 'garlic'}
        missing_staples = []
        for ingredient_id, ingredient in self.ingredients.items():
            if (ingredient.name.lower().replace(' ', '_') in basic_staples and 
                ingredient_id not in available_ingredients):
                missing_staples.append(ingredient.name)
        
        if missing_staples:
            recommendations.append(f"Consider stocking basic staples: {', '.join(missing_staples[:3])}")
        
        return recommendations
    
    def _get_substitution_recommendations(self, request: RecipeSuggestionRequest, 
                                        matches: List[RecipeMatch]) -> List[Dict[str, Any]]:
        """Get ingredient substitution recommendations."""
        available_ingredients = set(self._normalize_ingredient_identifiers(set(request.available_ingredients)))
        substitution_recommendations = []
        
        # Collect all missing ingredients that could be substituted
        substitution_candidates = set()
        for match in matches:
            substitution_candidates.update(match.missing_ingredients)
        
        for missing_ingredient_id in substitution_candidates:
            substitutes = self.ingredient_graph.find_ingredient_substitutes(
                missing_ingredient_id, available_ingredients
            )
            
            if substitutes:
                missing_ingredient = self.ingredients.get(missing_ingredient_id)
                if missing_ingredient:
                    best_substitutes = substitutes[:3]  # Top 3 substitutes
                    
                    substitution_recommendations.append({
                        'missing_ingredient': {
                            'id': missing_ingredient_id,
                            'name': missing_ingredient.name
                        },
                        'substitutes': [
                            {
                                'id': sub_id,
                                'name': self.ingredients.get(sub_id, {}).name if sub_id in self.ingredients else sub_id,
                                'similarity_score': similarity,
                                'substitution_notes': self._generate_substitution_notes(missing_ingredient_id, sub_id)
                            }
                            for sub_id, similarity in best_substitutes
                        ]
                    })
        
        return substitution_recommendations
    
    def _generate_substitution_notes(self, original_id: str, substitute_id: str) -> str:
        """Generate notes about ingredient substitution."""
        if original_id not in self.ingredients or substitute_id not in self.ingredients:
            return "Substitution may affect flavor profile."
        
        original = self.ingredients[original_id]
        substitute = self.ingredients[substitute_id]
        
        notes = []
        
        # Category match
        if original.category == substitute.category:
            notes.append("Same category - good substitute")
        else:
            notes.append(f"Different category ({original.category.value} → {substitute.category.value})")
        
        # Flavor impact
        flavor_diff = abs(original.flavor_profile.sweetness - substitute.flavor_profile.sweetness)
        if flavor_diff > 3:
            notes.append("May significantly change sweetness")
        
        # Dietary compatibility
        original_tags = set(original.dietary_tags)
        substitute_tags = set(substitute.dietary_tags)
        if not original_tags.issubset(substitute_tags):
            missing_tags = original_tags - substitute_tags
            notes.append(f"May not be suitable for: {', '.join(missing_tags)}")
        
        return "; ".join(notes) if notes else "Good general substitute"
    
    def _get_algorithm_insights(self, algorithm: str, request: RecipeSuggestionRequest) -> Dict[str, Any]:
        """Get insights about the algorithm used."""
        base_insights = {
            'algorithm_used': algorithm,
            'selection_reason': self._explain_algorithm_selection(algorithm, request)
        }
        
        if algorithm == "greedy" and self.greedy_matcher:
            base_insights.update(self.greedy_matcher.get_algorithm_insights())
        elif algorithm == "backtracking" and self.backtracking_matcher:
            base_insights.update(self.backtracking_matcher.get_algorithm_insights())
        elif algorithm == "graph":
            base_insights.update({
                'graph_statistics': self.ingredient_graph.get_graph_statistics(),
                'centrality_analysis': 'available'
            })
        
        return base_insights
    
    def _explain_algorithm_selection(self, algorithm: str, request: RecipeSuggestionRequest) -> str:
        """Explain why a particular algorithm was selected."""
        if request.algorithm_preference:
            return f"User requested {algorithm} algorithm"
        
        num_recipes = len(self.recipes)
        num_ingredients = len(request.available_ingredients)
        
        if algorithm == "greedy":
            return f"Selected for speed with {num_recipes} recipes and {num_ingredients} ingredients"
        elif algorithm == "backtracking":
            return f"Selected for optimal results with small dataset ({num_recipes} recipes)"
        elif algorithm == "graph":
            return "Selected for relationship-based analysis"
        else:
            return "Default selection"
    
    def _normalize_ingredient_identifiers(self, ingredient_names: Set[str]) -> Set[str]:
        """Convert ingredient names to IDs if needed."""
        normalized_ids = set()
        
        for name in ingredient_names:
            if name in self.ingredients:
                normalized_ids.add(name)
            else:
                # Find by name or alias
                for ingredient_id, ingredient in self.ingredients.items():
                    if (ingredient.name.lower() == name.lower() or 
                        name.lower() in [alias.lower() for alias in ingredient.aliases]):
                        normalized_ids.add(ingredient_id)
                        break
        
        return normalized_ids
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by its ID."""
        return self.recipes.get(recipe_id)
    
    def get_ingredient_by_id(self, ingredient_id: str) -> Optional[Ingredient]:
        """Get an ingredient by its ID."""
        return self.ingredients.get(ingredient_id)
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get statistics about the system."""
        return {
            'total_recipes': len(self.recipes),
            'total_ingredients': len(self.ingredients),
            'graph_statistics': self.ingredient_graph.get_graph_statistics(),
            'algorithm_availability': {
                'greedy': self.greedy_matcher is not None,
                'backtracking': self.backtracking_matcher is not None,
                'graph': True
            }
        } 