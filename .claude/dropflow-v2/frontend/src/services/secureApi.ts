/**
 * Secure API Client - TypeScript
 * Intègre: CSRF tokens, validation d'entrée, gestion d'erreur sécurisée
 */

import { Stats, Product, Store } from '../types';
import { validators } from '../utils/validators';
import { csrfUtils } from '../utils/csrf';
import { errorHandler } from '../utils/errorHandler';

const API_BASE = process.env.VITE_API_URL || 'http://localhost:8000';

export const secureApi = {
  /**
   * GET Stats avec gestion d'erreur
   */
  async getStats(): Promise<Stats> {
    try {
      const res = await csrfUtils.secureFetch(`${API_BASE}/stats`);
      if (!res.ok) throw await errorHandler.handleApiError(res);
      return res.json();
    } catch (error) {
      errorHandler.log(error, 'getStats');
      throw error;
    }
  },

  /**
   * GET Stores avec gestion d'erreur
   */
  async getStores(): Promise<Store[]> {
    try {
      const res = await csrfUtils.secureFetch(`${API_BASE}/stores`);
      if (!res.ok) throw await errorHandler.handleApiError(res);
      return res.json();
    } catch (error) {
      errorHandler.log(error, 'getStores');
      throw error;
    }
  },

  /**
   * GET Products avec gestion d'erreur
   */
  async getProducts(): Promise<Product[]> {
    try {
      const res = await csrfUtils.secureFetch(`${API_BASE}/products`);
      if (!res.ok) throw await errorHandler.handleApiError(res);
      return res.json();
    } catch (error) {
      errorHandler.log(error, 'getProducts');
      throw error;
    }
  },

  /**
   * POST Pipeline avec validation de niche
   */
  async runPipeline(niche: string): Promise<any> {
    try {
      // SÉCURITÉ: Valider l'entrée
      const validation = validators.niche(niche);
      if (!validation.valid) {
        const error = new Error(validation.error);
        error.name = 'ValidationError';
        throw error;
      }

      const res = await csrfUtils.secureFetch(
        `${API_BASE}/pipeline?niche=${encodeURIComponent(niche)}`,
        { method: 'POST' }
      );

      if (!res.ok) throw await errorHandler.handleApiError(res);
      return res.json();
    } catch (error) {
      errorHandler.log(error, 'runPipeline');
      throw error;
    }
  },

  /**
   * POST Find Product avec validation
   */
  async findProduct(niche: string): Promise<Product> {
    try {
      const validation = validators.niche(niche);
      if (!validation.valid) {
        const error = new Error(validation.error);
        error.name = 'ValidationError';
        throw error;
      }

      const res = await csrfUtils.secureFetch(
        `${API_BASE}/find-product?niche=${encodeURIComponent(niche)}`,
        { method: 'POST' }
      );

      if (!res.ok) throw await errorHandler.handleApiError(res);
      return res.json();
    } catch (error) {
      errorHandler.log(error, 'findProduct');
      throw error;
    }
  },

  /**
   * POST Find Supplier avec validation
   */
  async findSupplier(productName: string): Promise<any> {
    try {
      const validation = validators.text(productName, 2, 200);
      if (!validation.valid) {
        const error = new Error(validation.error);
        error.name = 'ValidationError';
        throw error;
      }

      const res = await csrfUtils.secureFetch(
        `${API_BASE}/find-supplier?product_name=${encodeURIComponent(productName)}`,
        { method: 'POST' }
      );

      if (!res.ok) throw await errorHandler.handleApiError(res);
      return res.json();
    } catch (error) {
      errorHandler.log(error, 'findSupplier');
      throw error;
    }
  },

  /**
   * POST Create Store avec validation complète
   */
  async createStore(productName: string, aliexpressUrl: string): Promise<Store> {
    try {
      // Valider les entrées
      const productValidation = validators.text(productName, 2, 200);
      if (!productValidation.valid) {
        const error = new Error(productValidation.error);
        error.name = 'ValidationError';
        throw error;
      }

      const urlValidation = validators.url(aliexpressUrl);
      if (!urlValidation.valid) {
        const error = new Error(urlValidation.error);
        error.name = 'ValidationError';
        throw error;
      }

      const res = await csrfUtils.secureFetch(`${API_BASE}/create-store`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          product_name: productName,
          niche: 'general',
          aliexpress_url: aliexpressUrl,
          budget_daily: 15.0
        })
      });

      if (!res.ok) throw await errorHandler.handleApiError(res);
      return res.json();
    } catch (error) {
      errorHandler.log(error, 'createStore');
      throw error;
    }
  },

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/health`);
      return res.ok;
    } catch {
      return false;
    }
  }
};
