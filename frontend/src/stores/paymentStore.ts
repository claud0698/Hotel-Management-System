/**
 * Payment Store
 * Manages payment data and operations
 */

import { create } from 'zustand';
import type { Payment } from '../services/api';
import { apiClient } from '../services/api';

interface PaymentState {
  payments: Payment[];
  selectedPayment: Payment | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchPayments: (reservationId?: number) => Promise<void>;
  fetchPayment: (id: number) => Promise<void>;
  createPayment: (data: Partial<Payment>) => Promise<Payment>;
  updatePayment: (id: number, data: Partial<Payment>) => Promise<Payment>;
  deletePayment: (id: number) => Promise<void>;
  setSelectedPayment: (payment: Payment | null) => void;
  clearError: () => void;
}

export const usePaymentStore = create<PaymentState>((set) => ({
  payments: [],
  selectedPayment: null,
  isLoading: false,
  error: null,

  fetchPayments: async (reservationId?: number) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getPayments(reservationId);
      set({
        payments: response.payments || [],
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch payments';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  fetchPayment: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getPayment(id);
      set({
        selectedPayment: response.payment,
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch payment';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  createPayment: async (data: Partial<Payment>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.createPayment(data);
      set((state) => ({
        payments: [...state.payments, response.payment],
        isLoading: false,
      }));
      return response.payment;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create payment';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  updatePayment: async (id: number, data: Partial<Payment>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.updatePayment(id, data);
      set((state) => ({
        payments: state.payments.map((p) => (p.id === id ? response.payment : p)),
        selectedPayment: state.selectedPayment?.id === id ? response.payment : state.selectedPayment,
        isLoading: false,
      }));
      return response.payment;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update payment';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  deletePayment: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.deletePayment(id);
      set((state) => ({
        payments: state.payments.filter((p) => p.id !== id),
        selectedPayment: state.selectedPayment?.id === id ? null : state.selectedPayment,
        isLoading: false,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete payment';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  setSelectedPayment: (payment: Payment | null) => set({ selectedPayment: payment }),
  clearError: () => set({ error: null }),
}));
