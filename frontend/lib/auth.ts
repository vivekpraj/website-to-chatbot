const TOKEN_KEY = "access_token";

export function saveToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export function getToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(TOKEN_KEY);
}

export function logout() {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
    window.location.href = "/login";
  }
}

/**
 * Decode JWT payload safely
 */
function decodeToken(token: string): any | null {
  try {
    const payload = token.split(".")[1];
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
}

/**
 * Get logged-in user's role
 * returns: "client" | "super_admin" | null
 */
export function getUserRole(): string | null {
  const token = getToken();
  if (!token) return null;

  const decoded = decodeToken(token);
  return decoded?.role || null;
}

/**
 * Get logged-in user id (optional, useful later)
 */
export function getUserId(): number | null {
  const token = getToken();
  if (!token) return null;

  const decoded = decodeToken(token);
  return decoded?.user_id || null;
}


/**
 * Check login state
 */
export function isAuthenticated(): boolean {
  return !!getToken();
}



