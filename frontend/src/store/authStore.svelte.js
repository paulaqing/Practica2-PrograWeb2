function decodeToken(token) {
    if (!token) return null;
    try {
        const base64Url = token.split('.')[1];
        if (!base64Url) return null;
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const padLen = (4 - (base64.length % 4)) % 4;
        const padded = base64 + '='.repeat(padLen);
        const jsonPayload = decodeURIComponent(
            atob(padded)
                .split('')
                .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                .join('')
        );
        return JSON.parse(jsonPayload);
    } catch (e) {
        console.error("Error al decodificar token JWT:", e);
        return null;
    }
}

export function createAuthStore() {
    let token = $state(localStorage.getItem('token') || null);
    let user = $state(null);

    // Initialize user if token exists (basic decode or fetch profile)
    if (token) {
        const payload = decodeToken(token);
        if (payload) {
            user = { id: payload.id, username: payload.username, role: payload.role };
        } else {
            token = null;
            localStorage.removeItem('token');
        }
    }

    return {
        get token() { return token; },
        get user() { return user; },
        get isAuthenticated() { return !!token; },
        login: (newToken, userData) => {
            token = newToken;
            localStorage.setItem('token', newToken);
            
            // Siempre decodificamos el token para extraer el rol y el ID reales
            const payload = decodeToken(newToken);
            if (payload) {
                user = { id: payload.id, username: payload.username, role: payload.role };
            } else {
                user = userData;
            }
        },
        logout: () => {
            token = null;
            user = null;
            localStorage.removeItem('token');
        }
    };
}

export const authState = createAuthStore();
