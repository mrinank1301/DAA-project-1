import networkx as nx
import numpy as np
from typing import List, Dict, Set, Tuple, Optional, Any
from collections import defaultdict, deque
import math
from sklearn.metrics.pairwise import cosine_similarity
from models.ingredient import Ingredient, IngredientCompatibility, FlavorProfile
from models.recipe import Recipe, RecipeMatch
import logging

logger = logging.getLogger(__name__)


class IngredientGraph:
    """
    Graph-based representation of ingredient relationships using NetworkX.
    Implements graph theory algorithms for recipe recommendation.
    """
    
    def __init__(self):
        self.graph = nx.Graph()
        self.ingredient_nodes = {}  # ingredient_id -> Ingredient
        self.recipe_nodes = {}  # recipe_id -> Recipe
        self.compatibility_matrix = {}
        
    def add_ingredient(self, ingredient: Ingredient):
        """Add an ingredient as a node in the graph."""
        self.ingredient_nodes[ingredient.id] = ingredient
        self.graph.add_node(ingredient.id, 
                           type='ingredient',
                           category=ingredient.category.value,
                           flavor_profile=ingredient.flavor_profile.dict(),
                           dietary_tags=ingredient.dietary_tags)
        
    def add_recipe(self, recipe: Recipe):
        """Add a recipe as a node and connect it to its ingredients."""
        self.recipe_nodes[recipe.id] = recipe
        self.graph.add_node(recipe.id,
                           type='recipe',
                           difficulty=recipe.difficulty.value,
                           cuisine=recipe.cuisine,
                           meal_types=[mt.value for mt in recipe.meal_types],
                           dietary_tags=recipe.dietary_tags)
        
        # Connect recipe to its ingredients
        for recipe_ingredient in recipe.ingredients:
            ingredient_id = recipe_ingredient.ingredient_id
            if ingredient_id in self.ingredient_nodes:
                # Weight based on quantity and importance
                weight = self._calculate_ingredient_importance(recipe_ingredient, recipe)
                self.graph.add_edge(recipe.id, ingredient_id, 
                                  weight=weight,
                                  relationship='recipe_ingredient',
                                  quantity=recipe_ingredient.quantity,
                                  unit=recipe_ingredient.unit,
                                  is_optional=recipe_ingredient.is_optional)
    
    def add_ingredient_compatibility(self, compatibility: IngredientCompatibility):
        """Add compatibility relationship between ingredients."""
        ingredient1_id = compatibility.ingredient1_id
        ingredient2_id = compatibility.ingredient2_id
        
        if ingredient1_id in self.ingredient_nodes and ingredient2_id in self.ingredient_nodes:
            self.graph.add_edge(ingredient1_id, ingredient2_id,
                              weight=compatibility.compatibility_score,
                              relationship='compatibility',
                              relationship_type=compatibility.relationship_type,
                              common_dishes=compatibility.common_dishes)
    
    def calculate_flavor_similarity(self, ingredient1_id: str, ingredient2_id: str) -> float:
        """Calculate flavor profile similarity between two ingredients."""
        if ingredient1_id not in self.ingredient_nodes or ingredient2_id not in self.ingredient_nodes:
            return 0.0
            
        ing1 = self.ingredient_nodes[ingredient1_id]
        ing2 = self.ingredient_nodes[ingredient2_id]
        
        # Convert flavor profiles to vectors
        profile1 = np.array([
            ing1.flavor_profile.sweetness,
            ing1.flavor_profile.saltiness,
            ing1.flavor_profile.sourness,
            ing1.flavor_profile.bitterness,
            ing1.flavor_profile.umami,
            ing1.flavor_profile.spiciness
        ]).reshape(1, -1)
        
        profile2 = np.array([
            ing2.flavor_profile.sweetness,
            ing2.flavor_profile.saltiness,
            ing2.flavor_profile.sourness,
            ing2.flavor_profile.bitterness,
            ing2.flavor_profile.umami,
            ing2.flavor_profile.spiciness
        ]).reshape(1, -1)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(profile1, profile2)[0][0]
        return max(0, similarity)  # Ensure non-negative
    
    def find_ingredient_substitutes(self, ingredient_id: str, available_ingredients: Set[str]) -> List[Tuple[str, float]]:
        """
        Find suitable substitutes for an ingredient using graph analysis.
        Returns list of (substitute_id, similarity_score) tuples.
        """
        if ingredient_id not in self.ingredient_nodes:
            return []
            
        target_ingredient = self.ingredient_nodes[ingredient_id]
        substitutes = []
        
        # Check direct substitutes first
        for substitute_id in target_ingredient.common_substitutes:
            if substitute_id in available_ingredients:
                similarity = self.calculate_flavor_similarity(ingredient_id, substitute_id)
                substitutes.append((substitute_id, similarity))
        
        # Find category-based substitutes
        for available_id in available_ingredients:
            if available_id in self.ingredient_nodes:
                available_ingredient = self.ingredient_nodes[available_id]
                
                # Same category bonus
                category_match = target_ingredient.category == available_ingredient.category
                flavor_similarity = self.calculate_flavor_similarity(ingredient_id, available_id)
                
                # Calculate combined score
                combined_score = flavor_similarity
                if category_match:
                    combined_score *= 1.2  # 20% bonus for same category
                
                # Check dietary compatibility
                dietary_compatible = not (
                    set(target_ingredient.dietary_tags) - set(available_ingredient.dietary_tags)
                )
                if not dietary_compatible:
                    combined_score *= 0.7  # Penalty for dietary incompatibility
                
                if combined_score > 0.3:  # Threshold for reasonable substitutes
                    substitutes.append((available_id, combined_score))
        
        # Sort by similarity score
        substitutes.sort(key=lambda x: x[1], reverse=True)
        return substitutes[:5]  # Return top 5 substitutes
    
    def calculate_recipe_match_score(self, recipe_id: str, available_ingredients: Set[str]) -> Dict[str, Any]:
        """
        Calculate how well a recipe matches available ingredients using graph analysis.
        """
        if recipe_id not in self.recipe_nodes:
            return {"score": 0.0, "analysis": {}}
            
        recipe = self.recipe_nodes[recipe_id]
        required_ingredients = {ri.ingredient_id for ri in recipe.ingredients if not ri.is_optional}
        optional_ingredients = {ri.ingredient_id for ri in recipe.ingredients if ri.is_optional}
        all_recipe_ingredients = required_ingredients.union(optional_ingredients)
        
        # Direct matches
        direct_matches = available_ingredients.intersection(all_recipe_ingredients)
        direct_required_matches = available_ingredients.intersection(required_ingredients)
        
        # Find substitutes for missing ingredients
        missing_required = required_ingredients - available_ingredients
        substitutable_ingredients = {}
        
        for missing_id in missing_required:
            substitutes = self.find_ingredient_substitutes(missing_id, available_ingredients)
            if substitutes:
                best_substitute, substitute_score = substitutes[0]
                substitutable_ingredients[missing_id] = {
                    'substitute': best_substitute,
                    'score': substitute_score
                }
        
        # Calculate match score
        total_required = len(required_ingredients)
        if total_required == 0:
            base_score = 1.0
        else:
            direct_score = len(direct_required_matches) / total_required
            substitute_score = sum(sub['score'] for sub in substitutable_ingredients.values()) / total_required
            base_score = direct_score + substitute_score * 0.8  # Substitutes get 80% weight
        
        # Bonus for optional ingredients
        optional_matches = available_ingredients.intersection(optional_ingredients)
        optional_bonus = len(optional_matches) / max(len(optional_ingredients), 1) * 0.1
        
        # Penalty for completely missing ingredients
        completely_missing = missing_required - set(substitutable_ingredients.keys())
        missing_penalty = len(completely_missing) / max(total_required, 1) * 0.3
        
        final_score = min(1.0, max(0.0, base_score + optional_bonus - missing_penalty))
        
        analysis = {
            'direct_matches': list(direct_matches),
            'missing_ingredients': list(completely_missing),
            'substitutable_ingredients': substitutable_ingredients,
            'optional_matches': list(optional_matches),
            'total_required_ingredients': total_required,
            'match_percentage': len(direct_required_matches) / max(total_required, 1)
        }
        
        return {"score": final_score, "analysis": analysis}
    
    def find_recipe_clusters(self, min_shared_ingredients: int = 3) -> Dict[str, List[str]]:
        """
        Find clusters of similar recipes based on shared ingredients.
        """
        recipe_ids = list(self.recipe_nodes.keys())
        clusters = defaultdict(list)
        
        for i, recipe1_id in enumerate(recipe_ids):
            for recipe2_id in recipe_ids[i+1:]:
                shared_ingredients = self._get_shared_ingredients(recipe1_id, recipe2_id)
                
                if len(shared_ingredients) >= min_shared_ingredients:
                    cluster_key = tuple(sorted(shared_ingredients))
                    clusters[cluster_key].extend([recipe1_id, recipe2_id])
        
        # Remove duplicates and create final clusters
        final_clusters = {}
        for i, (key, recipes) in enumerate(clusters.items()):
            unique_recipes = list(set(recipes))
            if len(unique_recipes) > 1:
                final_clusters[f"cluster_{i}"] = unique_recipes
        
        return final_clusters
    
    def get_ingredient_centrality(self) -> Dict[str, float]:
        """
        Calculate centrality measures for ingredients to identify key ingredients.
        """
        ingredient_subgraph = self.graph.subgraph(self.ingredient_nodes.keys())
        
        try:
            centrality = nx.betweenness_centrality(ingredient_subgraph, weight='weight')
            return centrality
        except:
            # Fallback to degree centrality if betweenness fails
            return nx.degree_centrality(ingredient_subgraph)
    
    def recommend_recipes_graph(self, available_ingredients: Set[str], 
                               max_results: int = 10) -> List[RecipeMatch]:
        """
        Recommend recipes using graph-based analysis.
        """
        recipe_scores = []
        
        for recipe_id in self.recipe_nodes.keys():
            match_result = self.calculate_recipe_match_score(recipe_id, available_ingredients)
            if match_result["score"] > 0.1:  # Minimum threshold
                recipe_scores.append((recipe_id, match_result["score"], match_result["analysis"]))
        
        # Sort by score
        recipe_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to RecipeMatch objects
        matches = []
        for recipe_id, score, analysis in recipe_scores[:max_results]:
            recipe = self.recipe_nodes[recipe_id]
            
            match = RecipeMatch(
                recipe=recipe,
                match_score=score,
                available_ingredients=analysis['direct_matches'],
                missing_ingredients=analysis['missing_ingredients'],
                substitutable_ingredients=list(analysis['substitutable_ingredients'].keys()),
                confidence_score=min(score * 1.2, 1.0),  # Slightly boost confidence
                algorithm_used="graph_theory",
                reasoning=f"Graph analysis found {len(analysis['direct_matches'])} direct matches "
                         f"and {len(analysis['substitutable_ingredients'])} substitutable ingredients"
            )
            matches.append(match)
        
        return matches
    
    def _calculate_ingredient_importance(self, recipe_ingredient, recipe: Recipe) -> float:
        """Calculate the importance/weight of an ingredient in a recipe."""
        base_weight = 1.0
        
        # Optional ingredients have lower weight
        if recipe_ingredient.is_optional:
            base_weight *= 0.5
        
        # Main ingredients (higher quantities) have higher weight
        # This is a simplified heuristic
        if recipe_ingredient.quantity > 100:  # Assuming grams
            base_weight *= 1.2
        
        return base_weight
    
    def _get_shared_ingredients(self, recipe1_id: str, recipe2_id: str) -> Set[str]:
        """Get ingredients shared between two recipes."""
        if recipe1_id not in self.recipe_nodes or recipe2_id not in self.recipe_nodes:
            return set()
        
        recipe1_ingredients = {ri.ingredient_id for ri in self.recipe_nodes[recipe1_id].ingredients}
        recipe2_ingredients = {ri.ingredient_id for ri in self.recipe_nodes[recipe2_id].ingredients}
        
        return recipe1_ingredients.intersection(recipe2_ingredients)
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the graph structure."""
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'ingredient_nodes': len(self.ingredient_nodes),
            'recipe_nodes': len(self.recipe_nodes),
            'average_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes() if self.graph.number_of_nodes() > 0 else 0,
            'density': nx.density(self.graph),
            'is_connected': nx.is_connected(self.graph) if self.graph.number_of_nodes() > 0 else False
        }
        
        return stats 