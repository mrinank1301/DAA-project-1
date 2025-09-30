// API Type Definitions for FlavorGraph

export type DifficultyLevel = "beginner" | "intermediate" | "advanced" | "expert";
export type MealType = "breakfast" | "lunch" | "dinner" | "snack" | "dessert" | "appetizer" | "beverage";
export type CookingMethod = "baking" | "boiling" | "frying" | "grilling" | "roasting" | "steaming" | "sauteing" | "braising" | "slow_cooking" | "raw";
export type IngredientCategory = "protein" | "vegetable" | "fruit" | "grain" | "dairy" | "spice" | "herb" | "condiment" | "fat" | "liquid" | "sweetener" | "nuts_seeds";

export interface FlavorProfile {
  sweetness: number;
  saltiness: number;
  sourness: number;
  bitterness: number;
  umami: number;
  spiciness: number;
}

export interface NutritionalInfo {
  calories_per_100g?: number;
  protein_g?: number;
  carbs_g?: number;
  fat_g?: number;
  fiber_g?: number;
  sugar_g?: number;
  sodium_mg?: number;
}

export interface Ingredient {
  id: string;
  name: string;
  category: IngredientCategory;
  aliases: string[];
  flavor_profile: FlavorProfile;
  nutritional_info: NutritionalInfo;
  common_substitutes: string[];
  dietary_tags: string[];
  storage_info?: string;
  season?: string[];
  origin?: string;
  cost_level?: number;
}

export interface RecipeIngredient {
  ingredient_id: string;
  quantity: number;
  unit: string;
  preparation?: string;
  is_optional: boolean;
  substitutes: string[];
}

export interface CookingStep {
  step_number: number;
  instruction: string;
  duration_minutes?: number;
  temperature?: string;
  equipment: string[];
  tips?: string;
}

export interface NutritionalSummary {
  total_calories?: number;
  servings: number;
  calories_per_serving?: number;
  protein_per_serving?: number;
  carbs_per_serving?: number;
  fat_per_serving?: number;
  fiber_per_serving?: number;
}

export interface Recipe {
  id: string;
  name: string;
  description?: string;
  cuisine?: string;
  meal_types: MealType[];
  difficulty: DifficultyLevel;
  cooking_methods: CookingMethod[];
  prep_time_minutes: number;
  cook_time_minutes: number;
  total_time_minutes: number;
  ingredients: RecipeIngredient[];
  instructions: CookingStep[];
  servings: number;
  nutritional_summary?: NutritionalSummary;
  dietary_tags: string[];
  tags: string[];
  equipment_needed: string[];
  average_rating?: number;
  rating_count: number;
  popularity_score: number;
  source?: string;
  author?: string;
  created_at?: string;
  updated_at?: string;
  ingredient_complexity_score?: number;
  technique_complexity_score?: number;
}

export interface RecipeMatch {
  recipe: Recipe;
  match_score: number;
  available_ingredients: string[];
  missing_ingredients: string[];
  substitutable_ingredients: string[];
  confidence_score: number;
  algorithm_used: string;
  reasoning?: string;
}

export interface RecipeSuggestionRequest {
  available_ingredients: string[];
  dietary_preferences?: string[];
  meal_type?: MealType;
  max_missing_ingredients?: number;
  max_prep_time?: number;
  max_cook_time?: number;
  difficulty_level?: DifficultyLevel;
  cuisine_preference?: string;
  exclude_ingredients?: string[];
  algorithm_preference?: string;
}

export interface RecipeSuggestionResponse {
  matches: RecipeMatch[];
  total_recipes_analyzed: number;
  analysis_time_ms: number;
  algorithm_insights: Record<string, any>;
  ingredient_gap_analysis: Record<string, any>;
  substitution_recommendations: Array<Record<string, any>>;
}

export interface SystemStats {
  status: string;
  service: string;
  algorithms: {
    graph_theory: string;
    backtracking: string;
    greedy: string;
  };
  data: {
    recipes_loaded: number;
    ingredients_loaded: number;
  };
} 