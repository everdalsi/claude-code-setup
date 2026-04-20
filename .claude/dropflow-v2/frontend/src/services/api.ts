import { Stats, Product, Store } from '../types';

const API_BASE = 'http://localhost:8000';

export const api = {
  async getStats(): Promise<Stats> {
    const res = await fetch(`${API_BASE}/stats`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  },

  async getStores(): Promise<Store[]> {
    const res = await fetch(`${API_BASE}/stores`);
    if (!res.ok) throw new Error('Failed to fetch stores');
    return res.json();
  },

  async getProducts(): Promise<Product[]> {
    const res = await fetch(`${API_BASE}/products`);
    if (!res.ok) throw new Error('Failed to fetch products');
    return res.json();
  },

  async runPipeline(niche: string): Promise<any> {
    const res = await fetch(`${API_BASE}/pipeline?niche=${encodeURIComponent(niche)}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Pipeline failed');
    return res.json();
  },

  async findProduct(niche: string): Promise<Product> {
    const res = await fetch(`${API_BASE}/find-product?niche=${encodeURIComponent(niche)}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Find product failed');
    return res.json();
  },

  async findSupplier(productName: string): Promise<any> {
    const res = await fetch(`${API_BASE}/find-supplier?product_name=${encodeURIComponent(productName)}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Find supplier failed');
    return res.json();
  },

  async createStore(productName: string, aliexpressUrl: string): Promise<Store> {
    const res = await fetch(`${API_BASE}/create-store`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_name: productName,
        niche: 'general',
        aliexpress_url: aliexpressUrl,
        budget_daily: 15.0
      })
    });
    if (!res.ok) throw new Error('Create store failed');
    return res.json();
  },

  async healthCheck(): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/health`);
      return res.ok;
    } catch {
      return false;
    }
  }
};
