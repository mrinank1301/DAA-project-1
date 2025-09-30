"use client";

import { useState } from "react";
import IngredientSelector from "@/components/IngredientSelector";
import RecipeCard from "@/components/RecipeCard";
import LoadingSpinner from "@/components/LoadingSpinner";
import ErrorMessage from "@/components/ErrorMessage";
import { api } from "@/lib/api";
import { RecipeSuggestionResponse, DifficultyLevel, MealType } from "@/types/api";

export default function Home() {
  const [ingredients, setIngredients] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<RecipeSuggestionResponse | null>(null);
  
  // Filter states
  const [dietaryPreferences, setDietaryPreferences] = useState<string[]>([]);
  const [mealType, setMealType] = useState<MealType | "">("");
  const [maxMissingIngredients, setMaxMissingIngredients] = useState(3);
  const [difficultyLevel, setDifficultyLevel] = useState<DifficultyLevel | "">("");
  const [maxPrepTime, setMaxPrepTime] = useState<number | "">("");

  const handleSearch = async () => {
    if (ingredients.length === 0) {
      setError("Please add at least one ingredient");
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await api.suggestRecipes({
        available_ingredients: ingredients,
        dietary_preferences: dietaryPreferences,
        meal_type: mealType || undefined,
        max_missing_ingredients: maxMissingIngredients,
        difficulty_level: difficultyLevel || undefined,
        max_prep_time: maxPrepTime || undefined,
      });
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch recipes");
    } finally {
      setLoading(false);
    }
  };

  const commonDietaryTags = ["vegetarian", "vegan", "gluten-free", "dairy-free", "low-carb", "keto"];

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            🍳 <span className="bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-teal-600">FlavorGraph</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Discover perfect recipes based on your available ingredients using intelligent algorithms
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Powered by Graph Theory, Backtracking & Greedy Algorithms
          </p>
        </div>

        {/* Search Section */}
        <div className="bg-white rounded-xl shadow-lg p-6 md:p-8 mb-8">
          <div className="space-y-6">
            {/* Ingredients Input */}
            <div>
              <label className="block text-lg font-semibold text-gray-700 mb-3">
                What ingredients do you have?
              </label>
              <IngredientSelector
                selectedIngredients={ingredients}
                onIngredientsChange={setIngredients}
                placeholder="e.g., tomato, chicken, garlic..."
              />
            </div>

            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Dietary Preferences */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dietary Preferences
                </label>
                <div className="flex flex-wrap gap-2">
                  {commonDietaryTags.map((tag) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => {
                        setDietaryPreferences((prev) =>
                          prev.includes(tag)
                            ? prev.filter((t) => t !== tag)
                            : [...prev, tag]
                        );
                      }}
                      className={`px-3 py-1 text-sm rounded-full transition-colors ${
                        dietaryPreferences.includes(tag)
                          ? "bg-emerald-600 text-white"
                          : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>

              {/* Meal Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Meal Type
                </label>
                <select
                  value={mealType}
                  onChange={(e) => setMealType(e.target.value as MealType | "")}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-gray-900"
                >
                  <option value="">Any</option>
                  <option value="breakfast">Breakfast</option>
                  <option value="lunch">Lunch</option>
                  <option value="dinner">Dinner</option>
                  <option value="snack">Snack</option>
                  <option value="dessert">Dessert</option>
                  <option value="appetizer">Appetizer</option>
                </select>
              </div>

              {/* Difficulty Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Difficulty Level
                </label>
                <select
                  value={difficultyLevel}
                  onChange={(e) => setDifficultyLevel(e.target.value as DifficultyLevel | "")}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-gray-900"
                >
                  <option value="">Any</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                  <option value="expert">Expert</option>
                </select>
              </div>

              {/* Max Missing Ingredients */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Missing Ingredients: {maxMissingIngredients}
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={maxMissingIngredients}
                  onChange={(e) => setMaxMissingIngredients(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              {/* Max Prep Time */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Prep Time (minutes)
                </label>
                <input
                  type="number"
                  value={maxPrepTime}
                  onChange={(e) => setMaxPrepTime(e.target.value ? Number(e.target.value) : "")}
                  placeholder="Any"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-gray-900 placeholder:text-gray-400"
                />
              </div>
            </div>

            {/* Search Button */}
            <button
              onClick={handleSearch}
              disabled={loading || ingredients.length === 0}
              className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 text-white py-4 rounded-lg font-semibold text-lg hover:from-emerald-700 hover:to-teal-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
            >
              {loading ? "Searching..." : "Find Recipes 🔍"}
            </button>
          </div>
        </div>

        {/* Loading State */}
        {loading && <LoadingSpinner message="Finding the best recipes for you..." />}

        {/* Error State */}
        {error && <ErrorMessage message={error} onRetry={handleSearch} />}

        {/* Results */}
        {results && (
          <div className="space-y-6">
            {/* Analysis Info */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Analysis Results</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-emerald-50 rounded-lg">
                  <p className="text-3xl font-bold text-emerald-600">{results.matches.length}</p>
                  <p className="text-sm text-gray-600">Recipes Found</p>
                </div>
                <div className="text-center p-4 bg-teal-50 rounded-lg">
                  <p className="text-3xl font-bold text-teal-600">{results.total_recipes_analyzed}</p>
                  <p className="text-sm text-gray-600">Recipes Analyzed</p>
                </div>
                <div className="text-center p-4 bg-cyan-50 rounded-lg">
                  <p className="text-3xl font-bold text-cyan-600">{Math.round(results.analysis_time_ms)}ms</p>
                  <p className="text-sm text-gray-600">Analysis Time</p>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-3xl font-bold text-blue-600">
                    {results.algorithm_insights.algorithm_used || "Hybrid"}
                  </p>
                  <p className="text-sm text-gray-600">Algorithm Used</p>
                </div>
              </div>
            </div>

            {/* Recipe Cards */}
            {results.matches.length > 0 ? (
              <>
                <h2 className="text-3xl font-bold text-gray-800">Recommended Recipes</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {results.matches.map((match) => (
                    <RecipeCard key={match.recipe.id} recipe={match.recipe} match={match} />
                  ))}
                </div>
              </>
            ) : (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-8 text-center">
                <p className="text-amber-800 text-lg">
                  No recipes found matching your criteria. Try adjusting your filters or adding more ingredients.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
