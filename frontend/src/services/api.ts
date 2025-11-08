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

// ==================== AUTHENTICATION ====================
export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface User {
  id: number;
  username: string;
  email?: string;
  full_name?: string;
  phone?: string;
  role: 'admin' | 'user';
  status: 'active' | 'inactive';
  last_login?: string;
  created_at: string;
  updated_at: string;
}

// ==================== ROOM TYPES ====================
export interface RoomType {
  id: number;
  name: string;
  code: string;
  description?: string;
  base_capacity_adults: number;
  base_capacity_children: number;
  bed_config?: string;
  default_rate: number;
  amenities?: string;
  max_occupancy: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ==================== ROOMS ====================
export interface Room {
  id: number;
  room_number: string;
  floor: number;
  room_type_id: number;
  room_type?: RoomType;
  status: 'available' | 'occupied' | 'out_of_order';
  view_type?: string;
  notes?: string;
  custom_rate?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RoomImage {
  id: number;
  room_id: number;
  image_type: 'main_photo' | 'bedroom' | 'bathroom' | 'living_area' | 'amenities' | 'other';
  storage_location: 'local' | 's3' | 'gcs' | 'azure';
  image_path: string;
  file_size_bytes?: number;
  mime_type?: string;
  uploaded_by?: number;
  display_order?: number;
  created_at: string;
  updated_at: string;
}

// ==================== GUESTS ====================
export interface Guest {
  id: number;
  full_name: string;
  email?: string;
  phone?: string;
  phone_country_code?: string;
  id_type: 'passport' | 'driver_license' | 'national_id' | 'other';
  id_number: string;
  nationality?: string;
  birth_date?: string;
  is_vip: boolean;
  notes?: string;
  preferred_room_type_id?: number;
  created_at: string;
  updated_at: string;
}

export interface GuestImage {
  id: number;
  guest_id: number;
  image_type: 'id_photo' | 'passport' | 'other';
  image_path: string;
  storage_location: 'local' | 's3' | 'gcs' | 'azure';
  uploaded_at: string;
}

// ==================== RESERVATIONS ====================
export interface Reservation {
  id: number;
  guest_id: number;
  guest?: Guest;
  room_id: number;
  room?: Room;
  check_in_date: string;
  check_out_date: string;
  status: 'confirmed' | 'checked_in' | 'checked_out' | 'cancelled';
  total_amount: number;
  total_paid: number;
  balance: number;
  notes?: string;
  checked_in_by?: number;
  checked_out_by?: number;
  checked_in_at?: string;
  checked_out_at?: string;
  created_at: string;
  updated_at: string;
}

// ==================== PAYMENTS ====================
export interface Payment {
  id: number;
  reservation_id: number;
  reservation?: Reservation;
  amount: number;
  payment_type: 'full' | 'downpayment' | 'deposit' | 'adjustment';
  payment_method: 'cash' | 'card' | 'transfer' | 'check' | 'other';
  reference_number?: string;
  notes?: string;
  recorded_by?: number;
  created_at: string;
  updated_at: string;
}

export interface PaymentAttachment {
  id: number;
  payment_id: number;
  file_type: 'receipt' | 'invoice' | 'proof' | 'other';
  file_path: string;
  storage_location: 'local' | 's3' | 'gcs' | 'azure';
  file_size_bytes?: number;
  uploaded_at: string;
}

// ==================== DASHBOARD ====================
export interface DashboardMetrics {
  total_rooms: number;
  occupied_rooms: number;
  available_rooms: number;
  occupancy_rate: number;
  total_income: number;
  total_expenses: number;
  net_profit: number;
  start_date: string;
  end_date: string;
}

export interface DashboardToday {
  occupancy_count: number;
  check_ins_today: number;
  check_outs_today: number;
  revenue_today: number;
  reservations_count: number;
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

        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          // Try different error message formats from backend
          if (errorData.detail) {
            errorMessage = errorData.detail;
          } else if (errorData.message) {
            errorMessage = errorData.message;
          } else if (errorData.error) {
            errorMessage = errorData.error;
          } else if (typeof errorData === 'string') {
            errorMessage = errorData;
          }
        } catch {
          // If response is not JSON, use default message
        }
        throw new Error(errorMessage);
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

  // ==================== GUESTS ====================

  async getGuests(): Promise<{ guests: Guest[] }> {
    return this.request('/guests');
  }

  async getGuest(guestId: number): Promise<{ guest: Guest }> {
    return this.request(`/guests/${guestId}`);
  }

  async createGuest(data: Partial<Guest>): Promise<{ guest: Guest }> {
    return this.request('/guests', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateGuest(
    guestId: number,
    data: Partial<Guest>
  ): Promise<{ guest: Guest }> {
    return this.request(`/guests/${guestId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteGuest(guestId: number): Promise<{ message: string }> {
    return this.request(`/guests/${guestId}`, {
      method: 'DELETE',
    });
  }

  // ==================== RESERVATIONS ====================

  async checkAvailability(
    roomId: number,
    checkInDate: string,
    checkOutDate: string
  ): Promise<{ available: boolean }> {
    const params = new URLSearchParams();
    params.append('room_id', roomId.toString());
    params.append('check_in_date', checkInDate);
    params.append('check_out_date', checkOutDate);
    return this.request(`/reservations/availability?${params.toString()}`);
  }

  async getReservations(): Promise<{ reservations: Reservation[] }> {
    return this.request('/reservations');
  }

  async getReservation(reservationId: number): Promise<{ reservation: Reservation }> {
    return this.request(`/reservations/${reservationId}`);
  }

  async getReservationBalance(reservationId: number): Promise<{ balance: number; total_amount: number; total_paid: number }> {
    return this.request(`/reservations/${reservationId}/balance`);
  }

  async createReservation(data: Partial<Reservation>): Promise<{ reservation: Reservation }> {
    return this.request('/reservations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateReservation(
    reservationId: number,
    data: Partial<Reservation>
  ): Promise<{ reservation: Reservation }> {
    return this.request(`/reservations/${reservationId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async checkInReservation(
    reservationId: number,
    notes?: string
  ): Promise<{ reservation: Reservation }> {
    return this.request(`/reservations/${reservationId}/check-in`, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }

  async checkOutReservation(
    reservationId: number,
    notes?: string
  ): Promise<{ reservation: Reservation }> {
    return this.request(`/reservations/${reservationId}/check-out`, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }

  async cancelReservation(reservationId: number): Promise<{ message: string }> {
    return this.request(`/reservations/${reservationId}`, {
      method: 'DELETE',
    });
  }

  // ==================== PAYMENTS ====================

  async getPayments(reservationId?: number): Promise<{ payments: Payment[] }> {
    const params = new URLSearchParams();
    if (reservationId) params.append('reservation_id', reservationId.toString());

    const query = params.toString();
    return this.request(`/payments${query ? '?' + query : ''}`);
  }

  async getPayment(paymentId: number): Promise<{ payment: Payment }> {
    return this.request(`/payments/${paymentId}`);
  }

  async createPayment(data: Partial<Payment>): Promise<{ payment: Payment }> {
    return this.request('/payments', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updatePayment(
    paymentId: number,
    data: Partial<Payment>
  ): Promise<{ payment: Payment }> {
    return this.request(`/payments/${paymentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deletePayment(paymentId: number): Promise<{ message: string }> {
    return this.request(`/payments/${paymentId}`, {
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

  async getDashboardToday(): Promise<DashboardToday> {
    return this.request('/dashboard/today');
  }
}

export const apiClient = new ApiClient();
