/**
 * Error Handler - TypeScript
 * Sécurité: Gestion erreurs sans exposition de données sensibles
 */

export interface ErrorInfo {
  message: string;
  code?: string;
  timestamp: string;
}

const USER_MESSAGES: Record<string, string> = {
  'NetworkError': 'Erreur de connexion. Vérifiez votre internet.',
  'TimeoutError': 'Délai d\'expiration. Réessayez.',
  'NotFoundError': 'Ressource non trouvée.',
  'ValidationError': 'Données invalides. Vérifiez les champs.',
  'AuthError': 'Authentification requise.',
  'PermissionError': 'Accès refusé.',
  'ServerError': 'Erreur serveur. Réessayez plus tard.',
  'ConflictError': 'Conflit de données. Actualisez et réessayez.'
};

export const errorHandler = {
  /**
   * Obtenir message sûr pour affichage utilisateur
   */
  getSafeMessage(error: unknown): string {
    if (error instanceof Error) {
      const name = error.name || 'Error';
      return USER_MESSAGES[name] || USER_MESSAGES['ServerError'];
    }

    return 'Une erreur s\'est produite. Réessayez.';
  },

  /**
   * Parser erreur API et obtenir message sûr
   */
  async handleApiError(response: Response): Promise<Error> {
    const status = response.status;

    let message = 'Erreur serveur';
    if (status === 400) message = 'Requête invalide';
    else if (status === 401) message = 'Authentification requise';
    else if (status === 403) message = 'Accès refusé';
    else if (status === 404) message = 'Non trouvé';
    else if (status === 409) message = 'Conflit de données';
    else if (status >= 500) message = 'Erreur serveur';

    const error = new Error(message);
    error.name = `HTTP${status}`;

    return error;
  },

  /**
   * Logger erreur en dev, seulement message en prod
   */
  log(error: unknown, context: string = ''): ErrorInfo {
    const timestamp = new Date().toISOString();

    if (process.env.NODE_ENV === 'development') {
      console.error(`[${timestamp}] ${context}:`, error);
    }

    // En production, logger seulement le message sûr
    const safeMessage = this.getSafeMessage(error);
    return {
      message: safeMessage,
      timestamp
    };
  }
};
