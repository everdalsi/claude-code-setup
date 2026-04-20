/**
 * CSRF Protection - TypeScript
 * Sécurité: CSRF tokens sur toutes les requêtes POST/PUT/DELETE
 */

export const csrfUtils = {
  /**
   * Extraire le token CSRF du meta tag
   */
  getTokenFromMeta(): string | null {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta?.getAttribute('content') || null;
  },

  /**
   * Générer un token CSRF aléatoire (256-bit)
   */
  generateToken(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  },

  /**
   * Ajouter le token CSRF aux headers
   */
  addTokenToHeaders(headers: Record<string, string> = {}): Record<string, string> {
    const token = this.getTokenFromMeta() || sessionStorage.getItem('csrf_token');
    if (!token) {
      console.warn('⚠️ CSRF token not found');
      return headers;
    }

    return {
      ...headers,
      'X-CSRF-Token': token
    };
  },

  /**
   * Wrapper fetch sécurisé avec CSRF
   */
  async secureFetch(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const method = (options.method || 'GET').toUpperCase();

    // Ajouter CSRF token pour les requêtes state-changing
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
      options.headers = this.addTokenToHeaders(
        options.headers as Record<string, string>
      );
    }

    return fetch(url, options);
  },

  /**
   * Initialiser CSRF protection au démarrage
   */
  init(): void {
    // Générer un token si pas présent
    if (!sessionStorage.getItem('csrf_token')) {
      const token = this.generateToken();
      sessionStorage.setItem('csrf_token', token);
    }
  }
};
