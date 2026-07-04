const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function generateRecipe(userId: string, ingredients: string[], preferences?: any) {
  try {
    const response = await fetch(`${API_BASE_URL}/generate_recipe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        ingredients,
        preferences
      }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.recipe_markdown;
  } catch (error) {
    console.error("Failed to generate recipe:", error);
    throw error;
  }
}
