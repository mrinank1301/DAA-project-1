"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Recipe } from "@/types/api";
import LoadingSpinner from "@/components/LoadingSpinner";
import ErrorMessage from "@/components/ErrorMessage";

export default function RecipeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const recipeId = params.id as string;
  
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecipe = async () => {
      try {
        setLoading(true);
        const data = await api.getRecipe(recipeId);
        setRecipe(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch recipe");
      } finally {
        setLoading(false);
      }
    };

    fetchRecipe();
  }, [recipeId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 py-8">
        <div className="max-w-5xl mx-auto px-4">
          <LoadingSpinner message="Loading recipe details..." />
        </div>
      </div>
    );
  }

  if (error || !recipe) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 py-8">
        <div className="max-w-5xl mx-auto px-4">
          <ErrorMessage
            message={error || "Recipe not found"}
            onRetry={() => router.push("/")}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <button
          onClick={() => router.back()}
          className="mb-6 flex items-center gap-2 text-emerald-600 hover:text-emerald-700 font-medium"
        >
          ← Back to Results
        </button>

        {/* Recipe Header */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-8">
          <div className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white px-8 py-6">
            <div className="flex flex-wrap items-center gap-4 mb-4">
              <span className="px-3 py-1 bg-white/20 rounded-full text-sm font-medium">
                {recipe.cuisine || "Global"}
              </span>
              <span className="px-3 py-1 bg-white/20 rounded-full text-sm font-medium">
                {recipe.difficulty}
              </span>
              {recipe.meal_types.map((type) => (
                <span key={type} className="px-3 py-1 bg-white/20 rounded-full text-sm font-medium">
                  {type}
                </span>
              ))}
            </div>
            <h1 className="text-4xl font-bold mb-2">{recipe.name}</h1>
            {recipe.description && (
              <p className="text-emerald-50 text-lg">{recipe.description}</p>
            )}
          </div>

          <div className="px-8 py-6">
            {/* Quick Info Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-emerald-50 rounded-lg">
                <p className="text-2xl font-bold text-emerald-600">{recipe.prep_time_minutes}m</p>
                <p className="text-sm text-gray-600">Prep Time</p>
              </div>
              <div className="text-center p-4 bg-teal-50 rounded-lg">
                <p className="text-2xl font-bold text-teal-600">{recipe.cook_time_minutes}m</p>
                <p className="text-sm text-gray-600">Cook Time</p>
              </div>
              <div className="text-center p-4 bg-cyan-50 rounded-lg">
                <p className="text-2xl font-bold text-cyan-600">{recipe.total_time_minutes}m</p>
                <p className="text-sm text-gray-600">Total Time</p>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">{recipe.servings}</p>
                <p className="text-sm text-gray-600">Servings</p>
              </div>
            </div>

            {/* Rating */}
            {recipe.average_rating && (
              <div className="flex items-center gap-2 mb-6">
                <div className="flex items-center gap-1">
                  {[...Array(5)].map((_, i) => (
                    <span
                      key={i}
                      className={`text-xl ${
                        i < Math.round(recipe.average_rating!)
                          ? "text-yellow-500"
                          : "text-gray-300"
                      }`}
                    >
                      ★
                    </span>
                  ))}
                </div>
                <span className="text-gray-700 font-medium">
                  {recipe.average_rating.toFixed(1)} ({recipe.rating_count} reviews)
                </span>
              </div>
            )}

            {/* Dietary Tags */}
            {recipe.dietary_tags.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Dietary Information</h3>
                <div className="flex flex-wrap gap-2">
                  {recipe.dietary_tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-sm font-medium"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Nutritional Info */}
            {recipe.nutritional_summary && recipe.nutritional_summary.calories_per_serving && (
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h3 className="text-lg font-bold text-gray-800 mb-3">Nutritional Information (per serving)</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
                  {recipe.nutritional_summary.calories_per_serving && (
                    <div>
                      <p className="text-xl font-bold text-gray-800">
                        {Math.round(recipe.nutritional_summary.calories_per_serving)}
                      </p>
                      <p className="text-xs text-gray-600">Calories</p>
                    </div>
                  )}
                  {recipe.nutritional_summary.protein_per_serving && (
                    <div>
                      <p className="text-xl font-bold text-gray-800">
                        {recipe.nutritional_summary.protein_per_serving.toFixed(1)}g
                      </p>
                      <p className="text-xs text-gray-600">Protein</p>
                    </div>
                  )}
                  {recipe.nutritional_summary.carbs_per_serving && (
                    <div>
                      <p className="text-xl font-bold text-gray-800">
                        {recipe.nutritional_summary.carbs_per_serving.toFixed(1)}g
                      </p>
                      <p className="text-xs text-gray-600">Carbs</p>
                    </div>
                  )}
                  {recipe.nutritional_summary.fat_per_serving && (
                    <div>
                      <p className="text-xl font-bold text-gray-800">
                        {recipe.nutritional_summary.fat_per_serving.toFixed(1)}g
                      </p>
                      <p className="text-xs text-gray-600">Fat</p>
                    </div>
                  )}
                  {recipe.nutritional_summary.fiber_per_serving && (
                    <div>
                      <p className="text-xl font-bold text-gray-800">
                        {recipe.nutritional_summary.fiber_per_serving.toFixed(1)}g
                      </p>
                      <p className="text-xs text-gray-600">Fiber</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Ingredients Section */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Ingredients</h2>
          <ul className="space-y-3">
            {recipe.ingredients.map((ingredient, index) => (
              <li key={index} className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                <span className="flex-shrink-0 w-6 h-6 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center text-sm font-semibold">
                  {index + 1}
                </span>
                <div className="flex-1">
                  <span className="text-gray-800">
                    <span className="font-semibold">{ingredient.quantity} {ingredient.unit}</span>
                    {" "}{ingredient.ingredient_id}
                    {ingredient.preparation && (
                      <span className="text-gray-600 italic"> ({ingredient.preparation})</span>
                    )}
                  </span>
                  {ingredient.is_optional && (
                    <span className="ml-2 text-xs text-gray-500 italic">(optional)</span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>

        {/* Equipment Needed */}
        {recipe.equipment_needed.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Equipment Needed</h2>
            <div className="flex flex-wrap gap-3">
              {recipe.equipment_needed.map((equipment) => (
                <span
                  key={equipment}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium"
                >
                  {equipment}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Instructions Section */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Instructions</h2>
          <div className="space-y-6">
            {recipe.instructions.map((step) => (
              <div key={step.step_number} className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 text-white rounded-full flex items-center justify-center font-bold">
                    {step.step_number}
                  </div>
                </div>
                <div className="flex-1 pt-1">
                  <p className="text-gray-800 leading-relaxed mb-2">{step.instruction}</p>
                  <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                    {step.duration_minutes && (
                      <span>⏱️ {step.duration_minutes} minutes</span>
                    )}
                    {step.temperature && (
                      <span>🌡️ {step.temperature}</span>
                    )}
                  </div>
                  {step.tips && (
                    <div className="mt-2 p-3 bg-amber-50 border-l-4 border-amber-400 rounded">
                      <p className="text-sm text-amber-800">
                        <span className="font-semibold">💡 Tip:</span> {step.tips}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tags */}
        {recipe.tags.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Tags</h2>
            <div className="flex flex-wrap gap-2">
              {recipe.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 