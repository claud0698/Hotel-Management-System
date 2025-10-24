/**
 * Tenant Store
 * Manages tenant data and operations
 */

import { create } from 'zustand';
import type { Tenant } from '../services/api';
import { apiClient } from '../services/api';

interface TenantState {
  tenants: Tenant[];
  selectedTenant: Tenant | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchTenants: () => Promise<void>;
  fetchTenant: (id: number) => Promise<void>;
  createTenant: (data: Partial<Tenant>) => Promise<Tenant>;
  updateTenant: (id: number, data: Partial<Tenant>) => Promise<Tenant>;
  deleteTenant: (id: number) => Promise<void>;
  setSelectedTenant: (tenant: Tenant | null) => void;
  clearError: () => void;
}

export const useTenantStore = create<TenantState>((set) => ({
  tenants: [],
  selectedTenant: null,
  isLoading: false,
  error: null,

  fetchTenants: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getTenants();
      set({
        tenants: response.tenants || [],
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch tenants';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  fetchTenant: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getTenant(id);
      set({
        selectedTenant: response.tenant,
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch tenant';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  createTenant: async (data: Partial<Tenant>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.createTenant(data);
      set((state) => ({
        tenants: [...state.tenants, response.tenant],
        isLoading: false,
      }));
      return response.tenant;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create tenant';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  updateTenant: async (id: number, data: Partial<Tenant>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.updateTenant(id, data);
      set((state) => ({
        tenants: state.tenants.map((t) => (t.id === id ? response.tenant : t)),
        selectedTenant: state.selectedTenant?.id === id ? response.tenant : state.selectedTenant,
        isLoading: false,
      }));
      return response.tenant;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update tenant';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  deleteTenant: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.deleteTenant(id);
      set((state) => ({
        tenants: state.tenants.filter((t) => t.id !== id),
        selectedTenant: state.selectedTenant?.id === id ? null : state.selectedTenant,
        isLoading: false,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete tenant';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  setSelectedTenant: (tenant: Tenant | null) => set({ selectedTenant: tenant }),
  clearError: () => set({ error: null }),
}));
