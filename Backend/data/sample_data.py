from datetime import datetime
from typing import List
import asyncio

from models.ingredient import (
    Ingredient, IngredientCategory, FlavorProfile, NutritionalInfo, IngredientCompatibility
)
from models.recipe import (
    Recipe, RecipeIngredient, CookingStep, DifficultyLevel, CookingMethod, MealType, NutritionalSummary
)
from api.routes import recipe_service


async def load_sample_data():
    """Load sample ingredients and recipes into the system."""
    
    # Load ingredients first
    await load_sample_ingredients()
    
    # Then load recipes
    await load_sample_recipes()
    
    # Add ingredient compatibilities
    await load_ingredient_compatibilities()


async def load_sample_ingredients():
    """Load sample ingredients."""
    
    ingredients = [
        # Vegetables
        Ingredient(
            id="tomato_001",
            name="Tomato",
            category=IngredientCategory.VEGETABLE,
            aliases=["tomatoes", "fresh tomato", "ripe tomato"],
            flavor_profile=FlavorProfile(
                sweetness=6, saltiness=1, sourness=4, bitterness=1, umami=7, spiciness=0
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=18, protein_g=0.9, carbs_g=3.9, fat_g=0.2, fiber_g=1.2
            ),
            common_substitutes=["canned_tomato_001", "tomato_paste_001"],
            dietary_tags=["vegetarian", "vegan", "gluten-free", "keto"],
            season=["summer", "fall"],
            cost_level=2
        ),
        
        Ingredient(
            id="onion_001",
            name="Onion",
            category=IngredientCategory.VEGETABLE,
            aliases=["onions", "yellow onion", "white onion"],
            flavor_profile=FlavorProfile(
                sweetness=5, saltiness=1, sourness=2, bitterness=3, umami=6, spiciness=4
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=40, protein_g=1.1, carbs_g=9.3, fat_g=0.1, fiber_g=1.7
            ),
            common_substitutes=["shallot_001", "leek_001"],
            dietary_tags=["vegetarian", "vegan", "gluten-free", "keto"],
            cost_level=1
        ),
        
        Ingredient(
            id="garlic_001",
            name="Garlic",
            category=IngredientCategory.VEGETABLE,
            aliases=["garlic cloves", "fresh garlic"],
            flavor_profile=FlavorProfile(
                sweetness=2, saltiness=1, sourness=1, bitterness=2, umami=8, spiciness=6
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=149, protein_g=6.4, carbs_g=33.1, fat_g=0.5, fiber_g=2.1
            ),
            common_substitutes=["garlic_powder_001", "shallot_001"],
            dietary_tags=["vegetarian", "vegan", "gluten-free", "keto"],
            cost_level=2
        ),
        
        Ingredient(
            id="bell_pepper_001",
            name="Bell Pepper",
            category=IngredientCategory.VEGETABLE,
            aliases=["sweet pepper", "capsicum", "red pepper", "green pepper"],
            flavor_profile=FlavorProfile(
                sweetness=7, saltiness=0, sourness=1, bitterness=1, umami=3, spiciness=0
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=31, protein_g=1.0, carbs_g=7.3, fat_g=0.3, fiber_g=2.5
            ),
            dietary_tags=["vegetarian", "vegan", "gluten-free", "keto"],
            cost_level=3
        ),
        
        # Proteins
        Ingredient(
            id="chicken_breast_001",
            name="Chicken Breast",
            category=IngredientCategory.PROTEIN,
            aliases=["chicken", "chicken fillet", "boneless chicken"],
            flavor_profile=FlavorProfile(
                sweetness=1, saltiness=2, sourness=0, bitterness=0, umami=7, spiciness=0
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=165, protein_g=31.0, carbs_g=0, fat_g=3.6, fiber_g=0
            ),
            dietary_tags=["gluten-free", "keto"],
            cost_level=3
        ),
        
        Ingredient(
            id="ground_beef_001",
            name="Ground Beef",
            category=IngredientCategory.PROTEIN,
            aliases=["minced beef", "beef mince", "hamburger meat"],
            flavor_profile=FlavorProfile(
                sweetness=1, saltiness=3, sourness=0, bitterness=1, umami=9, spiciness=0
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=250, protein_g=26.0, carbs_g=0, fat_g=15.0, fiber_g=0
            ),
            dietary_tags=["gluten-free", "keto"],
            cost_level=4
        ),
        
        Ingredient(
            id="salmon_001",
            name="Salmon Fillet",
            category=IngredientCategory.PROTEIN,
            aliases=["salmon", "fresh salmon", "salmon steak"],
            flavor_profile=FlavorProfile(
                sweetness=2, saltiness=3, sourness=0, bitterness=0, umami=8, spiciness=0
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=208, protein_g=25.4, carbs_g=0, fat_g=12.4, fiber_g=0
            ),
            dietary_tags=["gluten-free", "keto"],
            cost_level=5
        ),
        
        # Grains
        Ingredient(
            id="pasta_001",
            name="Pasta",
            category=IngredientCategory.GRAIN,
            aliases=["spaghetti", "penne", "fusilli", "noodles"],
            flavor_profile=FlavorProfile(
                sweetness=3, saltiness=0, sourness=0, bitterness=0, umami=2, spiciness=0
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=371, protein_g=13.0, carbs_g=74.7, fat_g=1.5, fiber_g=3.2
            ),
            dietary_tags=["vegetarian"],
            cost_level=1
        ),
        
        Ingredient(
            id="rice_001",
            name="White Rice",
            category=IngredientCategory.GRAIN,
            aliases=["rice", "jasmine rice", "basmati rice"],
            flavor_profile=FlavorProfile(
                sweetness=4, saltiness=0, sourness=0, bitterness=0, umami=1, spiciness=0
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=365, protein_g=7.1, carbs_g=80.0, fat_g=0.7, fiber_g=1.3
            ),
            dietary_tags=["vegetarian", "vegan", "gluten-free"],
            cost_level=1
        ),
        
        # Dairy
        Ingredient(
            id="mozzarella_001",
            name="Mozzarella Cheese",
            category=IngredientCategory.DAIRY,
            aliases=["mozzarella", "fresh mozzarella", "cheese"],
            flavor_profile=FlavorProfile(
                sweetness=2, saltiness=4, sourness=1, bitterness=0, umami=8, spiciness=0
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=300, protein_g=22.2, carbs_g=2.2, fat_g=22.4, fiber_g=0
            ),
            dietary_tags=["vegetarian", "gluten-free", "keto"],
            cost_level=3
        ),
        
        Ingredient(
            id="parmesan_001",
            name="Parmesan Cheese",
            category=IngredientCategory.DAIRY,
            aliases=["parmigiano", "parmesan", "hard cheese"],
            flavor_profile=FlavorProfile(
                sweetness=1, saltiness=7, sourness=1, bitterness=1, umami=9, spiciness=0
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=431, protein_g=38.5, carbs_g=4.1, fat_g=29.0, fiber_g=0
            ),
            dietary_tags=["vegetarian", "gluten-free", "keto"],
            cost_level=4
        ),
        
        # Herbs and Spices
        Ingredient(
            id="basil_001",
            name="Fresh Basil",
            category=IngredientCategory.HERB,
            aliases=["basil", "sweet basil", "basil leaves"],
            flavor_profile=FlavorProfile(
                sweetness=4, saltiness=0, sourness=1, bitterness=2, umami=3, spiciness=3
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=22, protein_g=3.2, carbs_g=2.6, fat_g=0.6, fiber_g=1.6
            ),
            dietary_tags=["vegetarian", "vegan", "gluten-free", "keto"],
            cost_level=3
        ),
        
        Ingredient(
            id="oregano_001",
            name="Oregano",
            category=IngredientCategory.HERB,
            aliases=["dried oregano", "oregano leaves"],
            flavor_profile=FlavorProfile(
                sweetness=2, saltiness=0, sourness=1, bitterness=3, umami=4, spiciness=4
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=265, protein_g=9.0, carbs_g=68.9, fat_g=4.3, fiber_g=42.5
            ),
            dietary_tags=["vegetarian", "vegan", "gluten-free", "keto"],
            cost_level=2
        ),
        
        # Fats
        Ingredient(
            id="olive_oil_001",
            name="Olive Oil",
            category=IngredientCategory.FAT,
            aliases=["extra virgin olive oil", "EVOO", "cooking oil"],
            flavor_profile=FlavorProfile(
                sweetness=1, saltiness=0, sourness=1, bitterness=3, umami=2, spiciness=2
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=884, protein_g=0, carbs_g=0, fat_g=100.0, fiber_g=0
            ),
            dietary_tags=["vegetarian", "vegan", "gluten-free", "keto"],
            cost_level=3
        ),
        
        # Condiments
        Ingredient(
            id="salt_001",
            name="Salt",
            category=IngredientCategory.CONDIMENT,
            aliases=["table salt", "sea salt", "kosher salt"],
            flavor_profile=FlavorProfile(
                sweetness=0, saltiness=10, sourness=0, bitterness=0, umami=0, spiciness=0
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=0, protein_g=0, carbs_g=0, fat_g=0, fiber_g=0, sodium_mg=38758
            ),
            dietary_tags=["vegetarian", "vegan", "gluten-free", "keto"],
            cost_level=1
        ),
        
        Ingredient(
            id="black_pepper_001",
            name="Black Pepper",
            category=IngredientCategory.SPICE,
            aliases=["pepper", "ground black pepper", "peppercorns"],
            flavor_profile=FlavorProfile(
                sweetness=1, saltiness=0, sourness=0, bitterness=2, umami=1, spiciness=8
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=251, protein_g=10.4, carbs_g=63.9, fat_g=3.3, fiber_g=25.3
            ),
            dietary_tags=["vegetarian", "vegan", "gluten-free", "keto"],
            cost_level=2
        ),
        
        # Canned goods
        Ingredient(
            id="canned_tomato_001",
            name="Canned Tomatoes",
            category=IngredientCategory.VEGETABLE,
            aliases=["canned tomato", "tinned tomatoes", "crushed tomatoes"],
            flavor_profile=FlavorProfile(
                sweetness=5, saltiness=2, sourness=5, bitterness=1, umami=7, spiciness=0
            ),
            nutritional_info=NutritionalInfo(
                calories_per_100g=32, protein_g=1.6, carbs_g=7.0, fat_g=0.2, fiber_g=1.4
            ),
            common_substitutes=["tomato_001", "tomato_paste_001"],
            dietary_tags=["vegetarian", "vegan", "gluten-free", "keto"],
            cost_level=2
        )
    ]
    
    # Add all ingredients to the service
    for ingredient in ingredients:
        recipe_service.add_ingredient(ingredient)


async def load_sample_recipes():
    """Load sample recipes."""
    
    recipes = [
        # Classic Tomato Pasta
        Recipe(
            id="pasta_tomato_001",
            name="Classic Tomato Pasta",
            description="A simple and delicious pasta with fresh tomato sauce",
            cuisine="Italian",
            meal_types=[MealType.LUNCH, MealType.DINNER],
            difficulty=DifficultyLevel.BEGINNER,
            cooking_methods=[CookingMethod.BOILING, CookingMethod.SAUTEING],
            prep_time_minutes=10,
            cook_time_minutes=20,
            total_time_minutes=30,
            servings=4,
            ingredients=[
                RecipeIngredient(ingredient_id="pasta_001", quantity=400, unit="g"),
                RecipeIngredient(ingredient_id="tomato_001", quantity=500, unit="g", preparation="chopped"),
                RecipeIngredient(ingredient_id="onion_001", quantity=1, unit="medium", preparation="diced"),
                RecipeIngredient(ingredient_id="garlic_001", quantity=3, unit="cloves", preparation="minced"),
                RecipeIngredient(ingredient_id="olive_oil_001", quantity=30, unit="ml"),
                RecipeIngredient(ingredient_id="basil_001", quantity=10, unit="leaves", preparation="fresh"),
                RecipeIngredient(ingredient_id="salt_001", quantity=1, unit="tsp"),
                RecipeIngredient(ingredient_id="black_pepper_001", quantity=0.5, unit="tsp"),
                RecipeIngredient(ingredient_id="parmesan_001", quantity=50, unit="g", preparation="grated", is_optional=True)
            ],
            instructions=[
                CookingStep(step_number=1, instruction="Bring a large pot of salted water to boil", duration_minutes=5),
                CookingStep(step_number=2, instruction="Heat olive oil in a large pan over medium heat", duration_minutes=2),
                CookingStep(step_number=3, instruction="Add diced onion and cook until translucent", duration_minutes=5),
                CookingStep(step_number=4, instruction="Add minced garlic and cook for 1 minute", duration_minutes=1),
                CookingStep(step_number=5, instruction="Add chopped tomatoes, salt, and pepper. Simmer for 10 minutes", duration_minutes=10),
                CookingStep(step_number=6, instruction="Cook pasta according to package instructions", duration_minutes=8),
                CookingStep(step_number=7, instruction="Drain pasta and toss with tomato sauce", duration_minutes=2),
                CookingStep(step_number=8, instruction="Garnish with fresh basil and parmesan if desired", duration_minutes=1)
            ],
            dietary_tags=["vegetarian"],
            tags=["quick", "easy", "family-friendly", "italian"],
            equipment_needed=["large pot", "large pan", "colander"],
            average_rating=4.5,
            rating_count=127,
            popularity_score=0.8
        ),
        
        # Grilled Chicken with Vegetables
        Recipe(
            id="grilled_chicken_001",
            name="Grilled Chicken with Bell Peppers",
            description="Healthy grilled chicken breast with colorful bell peppers",
            cuisine="Mediterranean",
            meal_types=[MealType.LUNCH, MealType.DINNER],
            difficulty=DifficultyLevel.INTERMEDIATE,
            cooking_methods=[CookingMethod.GRILLING, CookingMethod.SAUTEING],
            prep_time_minutes=15,
            cook_time_minutes=25,
            total_time_minutes=40,
            servings=4,
            ingredients=[
                RecipeIngredient(ingredient_id="chicken_breast_001", quantity=600, unit="g"),
                RecipeIngredient(ingredient_id="bell_pepper_001", quantity=2, unit="large", preparation="sliced"),
                RecipeIngredient(ingredient_id="onion_001", quantity=1, unit="medium", preparation="sliced"),
                RecipeIngredient(ingredient_id="garlic_001", quantity=2, unit="cloves", preparation="minced"),
                RecipeIngredient(ingredient_id="olive_oil_001", quantity=45, unit="ml"),
                RecipeIngredient(ingredient_id="oregano_001", quantity=1, unit="tsp"),
                RecipeIngredient(ingredient_id="salt_001", quantity=1, unit="tsp"),
                RecipeIngredient(ingredient_id="black_pepper_001", quantity=0.5, unit="tsp")
            ],
            instructions=[
                CookingStep(step_number=1, instruction="Preheat grill to medium-high heat", duration_minutes=10),
                CookingStep(step_number=2, instruction="Season chicken with salt, pepper, and oregano", duration_minutes=5),
                CookingStep(step_number=3, instruction="Grill chicken for 6-7 minutes per side", duration_minutes=14),
                CookingStep(step_number=4, instruction="Heat oil in a pan, sauté onions and peppers", duration_minutes=8),
                CookingStep(step_number=5, instruction="Add garlic and cook for 1 minute", duration_minutes=1),
                CookingStep(step_number=6, instruction="Let chicken rest for 5 minutes, then slice", duration_minutes=5),
                CookingStep(step_number=7, instruction="Serve chicken with sautéed vegetables", duration_minutes=2)
            ],
            dietary_tags=["gluten-free", "keto", "high-protein"],
            tags=["healthy", "grilled", "mediterranean", "protein-rich"],
            equipment_needed=["grill", "large pan", "tongs"],
            average_rating=4.3,
            rating_count=89,
            popularity_score=0.7
        ),
        
        # Beef and Rice Bowl
        Recipe(
            id="beef_rice_bowl_001",
            name="Savory Beef and Rice Bowl",
            description="Hearty bowl with seasoned ground beef over rice",
            cuisine="Asian-inspired",
            meal_types=[MealType.LUNCH, MealType.DINNER],
            difficulty=DifficultyLevel.BEGINNER,
            cooking_methods=[CookingMethod.BOILING, CookingMethod.FRYING],
            prep_time_minutes=10,
            cook_time_minutes=30,
            total_time_minutes=40,
            servings=4,
            ingredients=[
                RecipeIngredient(ingredient_id="ground_beef_001", quantity=500, unit="g"),
                RecipeIngredient(ingredient_id="rice_001", quantity=300, unit="g"),
                RecipeIngredient(ingredient_id="onion_001", quantity=1, unit="medium", preparation="diced"),
                RecipeIngredient(ingredient_id="garlic_001", quantity=2, unit="cloves", preparation="minced"),
                RecipeIngredient(ingredient_id="olive_oil_001", quantity=15, unit="ml"),
                RecipeIngredient(ingredient_id="salt_001", quantity=1, unit="tsp"),
                RecipeIngredient(ingredient_id="black_pepper_001", quantity=0.5, unit="tsp")
            ],
            instructions=[
                CookingStep(step_number=1, instruction="Cook rice according to package instructions", duration_minutes=20),
                CookingStep(step_number=2, instruction="Heat oil in a large pan over medium-high heat", duration_minutes=2),
                CookingStep(step_number=3, instruction="Add ground beef and cook, breaking it up", duration_minutes=8),
                CookingStep(step_number=4, instruction="Add onion and cook until softened", duration_minutes=5),
                CookingStep(step_number=5, instruction="Add garlic, salt, and pepper. Cook 2 minutes", duration_minutes=2),
                CookingStep(step_number=6, instruction="Serve beef over rice in bowls", duration_minutes=3)
            ],
            dietary_tags=["gluten-free", "high-protein"],
            tags=["hearty", "filling", "comfort-food", "one-bowl"],
            equipment_needed=["rice cooker or pot", "large pan"],
            average_rating=4.1,
            rating_count=67,
            popularity_score=0.6
        ),
        
        # Caprese Salad (Simple recipe with few ingredients)
        Recipe(
            id="caprese_salad_001",
            name="Fresh Caprese Salad",
            description="Classic Italian salad with tomatoes, mozzarella, and basil",
            cuisine="Italian",
            meal_types=[MealType.LUNCH, MealType.APPETIZER],
            difficulty=DifficultyLevel.BEGINNER,
            cooking_methods=[CookingMethod.RAW],
            prep_time_minutes=10,
            cook_time_minutes=0,
            total_time_minutes=10,
            servings=4,
            ingredients=[
                RecipeIngredient(ingredient_id="tomato_001", quantity=3, unit="large", preparation="sliced"),
                RecipeIngredient(ingredient_id="mozzarella_001", quantity=250, unit="g", preparation="sliced"),
                RecipeIngredient(ingredient_id="basil_001", quantity=15, unit="leaves", preparation="fresh"),
                RecipeIngredient(ingredient_id="olive_oil_001", quantity=30, unit="ml"),
                RecipeIngredient(ingredient_id="salt_001", quantity=0.5, unit="tsp"),
                RecipeIngredient(ingredient_id="black_pepper_001", quantity=0.25, unit="tsp")
            ],
            instructions=[
                CookingStep(step_number=1, instruction="Arrange tomato and mozzarella slices alternately on a plate", duration_minutes=5),
                CookingStep(step_number=2, instruction="Tuck basil leaves between the slices", duration_minutes=2),
                CookingStep(step_number=3, instruction="Drizzle with olive oil", duration_minutes=1),
                CookingStep(step_number=4, instruction="Season with salt and pepper", duration_minutes=1),
                CookingStep(step_number=5, instruction="Let stand for 5 minutes before serving", duration_minutes=1)
            ],
            dietary_tags=["vegetarian", "gluten-free", "keto"],
            tags=["fresh", "no-cook", "italian", "light", "quick"],
            equipment_needed=["serving plate", "knife"],
            average_rating=4.7,
            rating_count=203,
            popularity_score=0.9
        ),
        
        # Salmon with Herbs
        Recipe(
            id="herb_salmon_001",
            name="Herb-Crusted Salmon",
            description="Baked salmon with fresh herbs and olive oil",
            cuisine="Mediterranean",
            meal_types=[MealType.DINNER],
            difficulty=DifficultyLevel.INTERMEDIATE,
            cooking_methods=[CookingMethod.BAKING],
            prep_time_minutes=15,
            cook_time_minutes=20,
            total_time_minutes=35,
            servings=4,
            ingredients=[
                RecipeIngredient(ingredient_id="salmon_001", quantity=600, unit="g"),
                RecipeIngredient(ingredient_id="basil_001", quantity=20, unit="leaves", preparation="chopped"),
                RecipeIngredient(ingredient_id="oregano_001", quantity=1, unit="tsp"),
                RecipeIngredient(ingredient_id="garlic_001", quantity=2, unit="cloves", preparation="minced"),
                RecipeIngredient(ingredient_id="olive_oil_001", quantity=30, unit="ml"),
                RecipeIngredient(ingredient_id="salt_001", quantity=1, unit="tsp"),
                RecipeIngredient(ingredient_id="black_pepper_001", quantity=0.5, unit="tsp")
            ],
            instructions=[
                CookingStep(step_number=1, instruction="Preheat oven to 200°C (400°F)", duration_minutes=10, temperature="200°C"),
                CookingStep(step_number=2, instruction="Mix herbs, garlic, and olive oil in a bowl", duration_minutes=3),
                CookingStep(step_number=3, instruction="Season salmon with salt and pepper", duration_minutes=2),
                CookingStep(step_number=4, instruction="Spread herb mixture over salmon", duration_minutes=3),
                CookingStep(step_number=5, instruction="Bake for 15-18 minutes until flaky", duration_minutes=18, temperature="200°C"),
                CookingStep(step_number=6, instruction="Let rest for 2 minutes before serving", duration_minutes=2)
            ],
            dietary_tags=["gluten-free", "keto", "high-protein", "omega-3"],
            tags=["healthy", "baked", "herb-crusted", "elegant"],
            equipment_needed=["baking dish", "oven", "mixing bowl"],
            average_rating=4.6,
            rating_count=145,
            popularity_score=0.75
        )
    ]
    
    # Add all recipes to the service
    for recipe in recipes:
        recipe_service.add_recipe(recipe)


async def load_ingredient_compatibilities():
    """Load ingredient compatibility relationships."""
    
    compatibilities = [
        # Classic Italian combinations
        IngredientCompatibility(
            ingredient1_id="tomato_001",
            ingredient2_id="basil_001",
            compatibility_score=0.95,
            relationship_type="complementary",
            common_dishes=["caprese salad", "margherita pizza", "tomato sauce"]
        ),
        
        IngredientCompatibility(
            ingredient1_id="tomato_001",
            ingredient2_id="mozzarella_001",
            compatibility_score=0.92,
            relationship_type="complementary",
            common_dishes=["caprese salad", "pizza", "lasagna"]
        ),
        
        IngredientCompatibility(
            ingredient1_id="garlic_001",
            ingredient2_id="olive_oil_001",
            compatibility_score=0.88,
            relationship_type="complementary",
            common_dishes=["aglio e olio", "garlic bread", "most Mediterranean dishes"]
        ),
        
        # Aromatics base
        IngredientCompatibility(
            ingredient1_id="onion_001",
            ingredient2_id="garlic_001",
            compatibility_score=0.90,
            relationship_type="complementary",
            common_dishes=["most savory dishes", "soffritto", "mirepoix"]
        ),
        
        # Protein and herb combinations
        IngredientCompatibility(
            ingredient1_id="chicken_breast_001",
            ingredient2_id="oregano_001",
            compatibility_score=0.85,
            relationship_type="complementary",
            common_dishes=["Greek chicken", "herb-roasted chicken"]
        ),
        
        IngredientCompatibility(
            ingredient1_id="salmon_001",
            ingredient2_id="basil_001",
            compatibility_score=0.80,
            relationship_type="complementary",
            common_dishes=["herb-crusted salmon", "salmon pesto"]
        ),
        
        # Vegetable combinations
        IngredientCompatibility(
            ingredient1_id="bell_pepper_001",
            ingredient2_id="onion_001",
            compatibility_score=0.87,
            relationship_type="complementary",
            common_dishes=["stir-fry", "fajitas", "ratatouille"]
        ),
        
        # Cheese combinations
        IngredientCompatibility(
            ingredient1_id="parmesan_001",
            ingredient2_id="basil_001",
            compatibility_score=0.83,
            relationship_type="complementary",
            common_dishes=["pesto", "pasta dishes", "Italian salads"]
        )
    ]
    
    # Add compatibilities to the graph
    for compatibility in compatibilities:
        recipe_service.ingredient_graph.add_ingredient_compatibility(compatibility)


if __name__ == "__main__":
    # For testing the data loading
    asyncio.run(load_sample_data()) 