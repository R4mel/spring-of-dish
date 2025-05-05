const BASE = import.meta.env.VITE_API_URL || ""; // .env로 설정해두셨다면 그대로 사용

export async function authorize() {
  window.location.href = `${BASE}/authorize`;
}

export async function getProfile() {
  const res = await fetch(`${BASE}/profile`, { credentials: "include" });
  if (!res.ok) throw new Error();
  return res.json();
}

export async function getMessage() {
  const res = await fetch(`${BASE}/message`, { credentials: "include" });
  if (!res.ok) throw new Error();
  return res.json();
}

export async function logout() {
  const res = await fetch(`${BASE}/logout`, { credentials: "include" });
  if (!res.ok) throw new Error();
  return res.json();
}

export async function unlink() {
  const res = await fetch(`${BASE}/unlink`, { credentials: "include" });
  if (!res.ok) throw new Error();
  return res.json();
}

export async function generateRecipe(ingredients) {
  const res = await fetch(`${BASE}/generate-recipe`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ingredients }),
  });
  if (!res.ok) throw new Error();
  return res.json();
}

export async function saveRecipe(recipeId) {
  const res = await fetch(`${BASE}/save-recipe`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ recipe_id: recipeId }),
  });
  if (!res.ok) throw new Error();
  return res.json();
}