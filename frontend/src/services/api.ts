/**
 * API Client Service
 * Centralized API communication for all backend endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';

// Types for API responses
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    username: string;
    created_at: string;
  };
}

export interface User {
  id: number;
  username: string;
  created_at: string;
}

export interface Room {
  id: number;
  room_number: string;
  floor: number;  // Floor 2 = A (Atas/Upper), Floor 1 = B (Bawah/Lower)
  room_type: string;
  monthly_rate: number;
  status: 'available' | 'occupied' | 'maintenance';
  amenities?: string;
  current_tenant?: Tenant;
  created_at: string;
  updated_at: string;
}

export interface Tenant {
  id: number;
  name: string;
  phone?: string;
  email?: string;
  id_number?: string;
  move_in_date?: string;
  move_out_date?: string;
  current_room_id?: number;
  status: 'active' | 'inactive' | 'moved_out';
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Payment {
  id: number;
  tenant_id: number;
  amount: number;
  due_date: string;
  paid_date?: string;
  status: 'pending' | 'paid' | 'overdue';
  payment_method?: string;
  receipt_number?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Expense {
  id: number;
  date: string;
  category: string;
  amount: number;
  description?: string;
  receipt_url?: string;
  created_at: string;
  updated_at: string;
}

export interface DashboardMetrics {
  total_rooms: number;
  occupied_rooms: number;
  available_rooms: number;
  occupancy_rate: number;
  total_income: number;
  total_expenses: number;
  net_profit: number;
  overdue_count: number;
  overdue_amount: number;
  pending_count: number;
  start_date: string;
  end_date: string;
}

export interface DashboardSummary {
  recent_payments: Payment[];
  recent_expenses: Expense[];
  overdue_tenants: Array<{
    tenant: Tenant;
    payment: Payment;
  }>;
}

class ApiClient {
  private token: string | null = null;

  constructor() {
    // Load token from localStorage on initialization
    this.token = localStorage.getItem('access_token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        // Handle 401 Unauthorized - token expired or invalid
        if (response.status === 401) {
          this.clearToken();
          // Redirect to login page
          window.location.href = '/login';
          throw new Error('Session expired. Please login again.');
        }

        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      // Handle empty responses (e.g., 204 No Content)
      if (response.status === 204) {
        return {} as T;
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // ==================== AUTHENTICATION ====================

  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await this.request<{ access_token: string; token_type: string; user: User }>(
      '/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      }
    );

    if (response.access_token) {
      this.setToken(response.access_token);
    }

    return response;
  }

  async getCurrentUser(): Promise<{ user: User }> {
    return this.request('/auth/me');
  }

  // ==================== USERS ====================

  async getUsers(): Promise<{ users: User[] }> {
    return this.request('/users');
  }

  async getUser(userId: number): Promise<{ user: User }> {
    return this.request(`/users/${userId}`);
  }

  async createUser(data: { username: string; password: string }): Promise<{ message: string; user: User }> {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateUser(userId: number, data: { username?: string; password?: string }): Promise<{ message: string; user: User }> {
    return this.request(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteUser(userId: number): Promise<{ message: string }> {
    return this.request(`/users/${userId}`, {
      method: 'DELETE',
    });
  }

  // ==================== ROOMS ====================

  async getRooms(): Promise<{ rooms: Room[] }> {
    return this.request('/rooms');
  }

  async getRoom(roomId: number): Promise<{ room: Room }> {
    return this.request(`/rooms/${roomId}`);
  }

  async createRoom(data: Partial<Room>): Promise<{ message: string; room: Room }> {
    return this.request('/rooms', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateRoom(
    roomId: number,
    data: Partial<Room>
  ): Promise<{ message: string; room: Room }> {
    return this.request(`/rooms/${roomId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteRoom(roomId: number): Promise<{ message: string }> {
    return this.request(`/rooms/${roomId}`, {
      method: 'DELETE',
    });
  }

  // ==================== TENANTS ====================

  async getTenants(): Promise<{ tenants: Tenant[] }> {
    return this.request('/tenants');
  }

  async getTenant(tenantId: number): Promise<{ tenant: Tenant }> {
    return this.request(`/tenants/${tenantId}`);
  }

  async createTenant(data: Partial<Tenant>): Promise<{ message: string; tenant: Tenant }> {
    return this.request('/tenants', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTenant(
    tenantId: number,
    data: Partial<Tenant>
  ): Promise<{ message: string; tenant: Tenant }> {
    return this.request(`/tenants/${tenantId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteTenant(tenantId: number): Promise<{ message: string }> {
    return this.request(`/tenants/${tenantId}`, {
      method: 'DELETE',
    });
  }

  // ==================== PAYMENTS ====================

  async getPayments(
    tenantId?: number,
    status?: string
  ): Promise<{ payments: Payment[] }> {
    const params = new URLSearchParams();
    if (tenantId) params.append('tenant_id', tenantId.toString());
    if (status) params.append('status', status);

    const query = params.toString();
    return this.request(`/payments${query ? '?' + query : ''}`);
  }

  async getPayment(paymentId: number): Promise<{ payment: Payment }> {
    return this.request(`/payments/${paymentId}`);
  }

  async createPayment(data: Partial<Payment>): Promise<{ message: string; payment: Payment }> {
    return this.request('/payments', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updatePayment(
    paymentId: number,
    data: Partial<Payment>
  ): Promise<{ message: string; payment: Payment }> {
    return this.request(`/payments/${paymentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async markPaymentAsPaid(
    paymentId: number,
    paymentMethod?: string,
    receiptNumber?: string
  ): Promise<{ message: string; payment: Payment }> {
    return this.request(`/payments/${paymentId}/mark-paid`, {
      method: 'POST',
      body: JSON.stringify({
        payment_method: paymentMethod,
        receipt_number: receiptNumber,
      }),
    });
  }

  async deletePayment(paymentId: number): Promise<{ message: string }> {
    return this.request(`/payments/${paymentId}`, {
      method: 'DELETE',
    });
  }

  // ==================== EXPENSES ====================

  async getExpenses(
    category?: string,
    startDate?: string,
    endDate?: string
  ): Promise<{ expenses: Expense[] }> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const query = params.toString();
    return this.request(`/expenses${query ? '?' + query : ''}`);
  }

  async getExpense(expenseId: number): Promise<{ expense: Expense }> {
    return this.request(`/expenses/${expenseId}`);
  }

  async createExpense(data: Partial<Expense>): Promise<{ message: string; expense: Expense }> {
    return this.request('/expenses', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateExpense(
    expenseId: number,
    data: Partial<Expense>
  ): Promise<{ message: string; expense: Expense }> {
    return this.request(`/expenses/${expenseId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteExpense(expenseId: number): Promise<{ message: string }> {
    return this.request(`/expenses/${expenseId}`, {
      method: 'DELETE',
    });
  }

  // ==================== DASHBOARD ====================

  async getDashboardMetrics(
    startDate?: string,
    endDate?: string
  ): Promise<DashboardMetrics> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const query = params.toString();
    return this.request(`/dashboard/metrics${query ? '?' + query : ''}`);
  }

  async getDashboardSummary(): Promise<DashboardSummary> {
    return this.request('/dashboard/summary');
  }
}

export const apiClient = new ApiClient();
