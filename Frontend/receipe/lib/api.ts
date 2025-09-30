import {
  Recipe,
  Ingredient,
  RecipeSuggestionRequest,
  RecipeSuggestionResponse,
  SystemStats,
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error(`Network error: ${error instanceof Error ? error.message : "Unknown error"}`);
  }
}

export const api = {
  // Recipe endpoints
  suggestRecipes: async (request: RecipeSuggestionRequest): Promise<RecipeSuggestionResponse> => {
    return fetchApi<RecipeSuggestionResponse>("/recipes/suggest", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  getRecipe: async (recipeId: string): Promise<Recipe> => {
    return fetchApi<Recipe>(`/recipes/${recipeId}`);
  },

  listRecipes: async (params?: {
    limit?: number;
    offset?: number;
    cuisine?: string;
    meal_type?: string;
    difficulty?: string;
    max_prep_time?: number;
    dietary_tags?: string[];
  }): Promise<Recipe[]> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          if (Array.isArray(value)) {
            value.forEach(v => searchParams.append(key, v));
          } else {
            searchParams.append(key, String(value));
          }
        }
      });
    }
    const query = searchParams.toString();
    return fetchApi<Recipe[]>(`/recipes${query ? `?${query}` : ""}`);
  },

  getQuickRecipes: async (
    availableIngredients: string[],
    maxTimeMinutes: number = 30,
    maxResults: number = 5
  ) => {
    const params = new URLSearchParams();
    availableIngredients.forEach(ing => params.append("available_ingredients", ing));
    params.append("max_time_minutes", String(maxTimeMinutes));
    params.append("max_results", String(maxResults));
    return fetchApi(`/recipes/quick?${params.toString()}`);
  },

  getPopularRecipes: async (
    availableIngredients: string[],
    maxResults: number = 5
  ) => {
    const params = new URLSearchParams();
    availableIngredients.forEach(ing => params.append("available_ingredients", ing));
    params.append("max_results", String(maxResults));
    return fetchApi(`/recipes/popular?${params.toString()}`);
  },

  // Ingredient endpoints
  getIngredient: async (ingredientId: string): Promise<Ingredient> => {
    return fetchApi<Ingredient>(`/ingredients/${ingredientId}`);
  },

  listIngredients: async (params?: {
    limit?: number;
    offset?: number;
    category?: string;
    dietary_tags?: string[];
    search?: string;
  }): Promise<Ingredient[]> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          if (Array.isArray(value)) {
            value.forEach(v => searchParams.append(key, v));
          } else {
            searchParams.append(key, String(value));
          }
        }
      });
    }
    const query = searchParams.toString();
    return fetchApi<Ingredient[]>(`/ingredients${query ? `?${query}` : ""}`);
  },

  analyzeIngredients: async (request: RecipeSuggestionRequest) => {
    return fetchApi("/ingredients/analyze", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  getIngredientSubstitutes: async (
    ingredientId: string,
    availableIngredients: string[]
  ) => {
    const params = new URLSearchParams();
    availableIngredients.forEach(ing => params.append("available_ingredients", ing));
    return fetchApi(`/ingredients/${ingredientId}/substitutes?${params.toString()}`);
  },

  // System endpoints
  getSystemStats: async (): Promise<SystemStats> => {
    return fetchApi<SystemStats>("/health");
  },

  analyzeGraph: async (availableIngredients: string[]) => {
    return fetchApi("/graph/analyze", {
      method: "POST",
      body: JSON.stringify(availableIngredients),
    });
  },
};

export { ApiError }; 