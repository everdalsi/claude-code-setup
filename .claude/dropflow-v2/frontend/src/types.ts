export interface Product {
  id?: number;
  name: string;
  niche: string;
  searches: number;
  competition: number;
  margin: number;
  score: number;
}

export interface Store {
  id: number;
  product_name: string;
  niche: string;
  domain: string;
  status: 'pending' | 'active' | 'completed';
  created_at: string;
  revenue: number;
}

export interface Stats {
  total_products: number;
  total_stores: number;
  total_revenue: number;
  total_campaigns: number;
  uptime_hours: number;
  revenue_pending: number;
}

export interface PipelineStep {
  id: number;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  icon: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}
