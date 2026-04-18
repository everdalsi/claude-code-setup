/**
 * Input Validators - TypeScript
 * Sécurité: Validation d'entrée + XSS prevention
 */

export interface ValidationResult {
  valid: boolean;
  error?: string;
}

export const validators = {
  email(value: string): ValidationResult {
    const trimmed = value.trim();
    if (!trimmed) return { valid: false, error: 'Email requis' };

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmed)) {
      return { valid: false, error: 'Format email invalide' };
    }

    if (trimmed.length > 254) {
      return { valid: false, error: 'Email trop long' };
    }

    return { valid: true };
  },

  text(value: string, minLength: number = 1, maxLength: number = 1000): ValidationResult {
    const trimmed = value.trim();

    if (trimmed.length < minLength) {
      return { valid: false, error: `Minimum ${minLength} caractères requis` };
    }

    if (trimmed.length > maxLength) {
      return { valid: false, error: `Maximum ${maxLength} caractères` };
    }

    return { valid: true };
  },

  url(value: string): ValidationResult {
    const trimmed = value.trim();
    if (!trimmed) return { valid: false, error: 'URL requise' };

    try {
      new URL(trimmed);
      return { valid: true };
    } catch {
      return { valid: false, error: 'URL invalide' };
    }
  },

  niche(value: string): ValidationResult {
    const trimmed = value.trim();
    if (!trimmed) return { valid: false, error: 'Niche requise' };

    if (trimmed.length < 2) {
      return { valid: false, error: 'Niche trop court' };
    }

    if (!/^[a-zA-Z0-9\s\-_]+$/.test(trimmed)) {
      return { valid: false, error: 'Caractères invalides dans niche' };
    }

    return { valid: true };
  },

  sanitize(value: string): string {
    if (!value) return '';

    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;');
  }
};
