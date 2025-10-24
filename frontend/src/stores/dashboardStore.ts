/**
 * Dashboard Store
 * Manages dashboard metrics and summary data
 */

import { create } from 'zustand';
import type { DashboardMetrics, DashboardSummary } from '../services/api';
import { apiClient } from '../services/api';

interface DashboardState {
  metrics: DashboardMetrics | null;
  summary: DashboardSummary | null;
  isLoading: boolean;
  error: string | null;
  dateRange: {
    startDate?: string;
    endDate?: string;
  };

  // Actions
  fetchMetrics: (startDate?: string, endDate?: string) => Promise<void>;
  fetchSummary: () => Promise<void>;
  setDateRange: (startDate?: string, endDate?: string) => void;
  clearError: () => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  metrics: null,
  summary: null,
  isLoading: false,
  error: null,
  dateRange: {},

  fetchMetrics: async (startDate?: string, endDate?: string) => {
    set({ isLoading: true, error: null });
    try {
      const metrics = await apiClient.getDashboardMetrics(startDate, endDate);
      set({
        metrics,
        isLoading: false,
        dateRange: { startDate, endDate },
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch metrics';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  fetchSummary: async () => {
    set({ isLoading: true, error: null });
    try {
      const summary = await apiClient.getDashboardSummary();
      set({
        summary,
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch summary';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  setDateRange: (startDate?: string, endDate?: string) =>
    set({ dateRange: { startDate, endDate } }),

  clearError: () => set({ error: null }),
}));
