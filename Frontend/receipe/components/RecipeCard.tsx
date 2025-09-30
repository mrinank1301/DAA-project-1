import { Recipe, RecipeMatch } from "@/types/api";
import Link from "next/link";

interface RecipeCardProps {
  recipe: Recipe;
  match?: RecipeMatch;
}

export default function RecipeCard({ recipe, match }: RecipeCardProps) {
  return (
    <Link href={`/recipe/${recipe.id}`}>
      <div className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden border border-gray-200 h-full flex flex-col">
        {/* Header with cuisine and difficulty */}
        <div className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white px-4 py-3">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">{recipe.cuisine || "Global"}</span>
            <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
              {recipe.difficulty}
            </span>
          </div>
        </div>

        <div className="p-4 flex-1 flex flex-col">
          {/* Recipe name */}
          <h3 className="text-xl font-bold text-gray-800 mb-2 line-clamp-2">
            {recipe.name}
          </h3>

          {/* Description */}
          {recipe.description && (
            <p className="text-gray-600 text-sm mb-3 line-clamp-2 flex-1">
              {recipe.description}
            </p>
          )}

          {/* Match score if available */}
          {match && (
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">Match Score</span>
                <span className="text-sm font-bold text-emerald-600">
                  {Math.round(match.match_score * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-emerald-500 to-teal-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${match.match_score * 100}%` }}
                />
              </div>
              {match.missing_ingredients.length > 0 && (
                <p className="text-xs text-amber-600 mt-1">
                  Missing {match.missing_ingredients.length} ingredient{match.missing_ingredients.length !== 1 ? 's' : ''}
                </p>
              )}
            </div>
          )}

          {/* Time and servings info */}
          <div className="grid grid-cols-3 gap-2 mb-3 text-center">
            <div className="bg-gray-50 rounded p-2">
              <p className="text-xs text-gray-500">Prep</p>
              <p className="text-sm font-semibold text-gray-700">{recipe.prep_time_minutes}m</p>
            </div>
            <div className="bg-gray-50 rounded p-2">
              <p className="text-xs text-gray-500">Cook</p>
              <p className="text-sm font-semibold text-gray-700">{recipe.cook_time_minutes}m</p>
            </div>
            <div className="bg-gray-50 rounded p-2">
              <p className="text-xs text-gray-500">Servings</p>
              <p className="text-sm font-semibold text-gray-700">{recipe.servings}</p>
            </div>
          </div>

          {/* Dietary tags */}
          {recipe.dietary_tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {recipe.dietary_tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full"
                >
                  {tag}
                </span>
              ))}
              {recipe.dietary_tags.length > 3 && (
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                  +{recipe.dietary_tags.length - 3}
                </span>
              )}
            </div>
          )}

          {/* Rating */}
          {recipe.average_rating && (
            <div className="flex items-center gap-1 mt-auto">
              <span className="text-yellow-500">★</span>
              <span className="text-sm font-medium text-gray-700">
                {recipe.average_rating.toFixed(1)}
              </span>
              <span className="text-xs text-gray-500">
                ({recipe.rating_count})
              </span>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
} 