/**
 * Reservation Store
 * Manages reservation data and operations
 */

import { create } from 'zustand';
import type { Reservation } from '../services/api';
import { apiClient } from '../services/api';

interface ReservationState {
  reservations: Reservation[];
  selectedReservation: Reservation | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchReservations: () => Promise<void>;
  fetchReservation: (id: number) => Promise<void>;
  createReservation: (data: Partial<Reservation>) => Promise<Reservation>;
  updateReservation: (id: number, data: Partial<Reservation>) => Promise<Reservation>;
  checkInReservation: (id: number, notes?: string) => Promise<Reservation>;
  checkOutReservation: (id: number, notes?: string) => Promise<Reservation>;
  cancelReservation: (id: number) => Promise<void>;
  checkAvailability: (roomId: number, checkInDate: string, checkOutDate: string) => Promise<boolean>;
  setSelectedReservation: (reservation: Reservation | null) => void;
  clearError: () => void;
}

export const useReservationStore = create<ReservationState>((set) => ({
  reservations: [],
  selectedReservation: null,
  isLoading: false,
  error: null,

  fetchReservations: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getReservations();
      set({
        reservations: response.reservations || [],
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch reservations';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  fetchReservation: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getReservation(id);
      set({
        selectedReservation: response.reservation,
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch reservation';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  createReservation: async (data: Partial<Reservation>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.createReservation(data);
      set((state) => ({
        reservations: [...state.reservations, response.reservation],
        isLoading: false,
      }));
      return response.reservation;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create reservation';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  updateReservation: async (id: number, data: Partial<Reservation>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.updateReservation(id, data);
      set((state) => ({
        reservations: state.reservations.map((r) => (r.id === id ? response.reservation : r)),
        selectedReservation: state.selectedReservation?.id === id ? response.reservation : state.selectedReservation,
        isLoading: false,
      }));
      return response.reservation;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update reservation';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  checkInReservation: async (id: number, notes?: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.checkInReservation(id, notes);
      set((state) => ({
        reservations: state.reservations.map((r) => (r.id === id ? response.reservation : r)),
        selectedReservation: state.selectedReservation?.id === id ? response.reservation : state.selectedReservation,
        isLoading: false,
      }));
      return response.reservation;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to check in reservation';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  checkOutReservation: async (id: number, notes?: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.checkOutReservation(id, notes);
      set((state) => ({
        reservations: state.reservations.map((r) => (r.id === id ? response.reservation : r)),
        selectedReservation: state.selectedReservation?.id === id ? response.reservation : state.selectedReservation,
        isLoading: false,
      }));
      return response.reservation;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to check out reservation';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  cancelReservation: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.cancelReservation(id);
      set((state) => ({
        reservations: state.reservations.filter((r) => r.id !== id),
        selectedReservation: state.selectedReservation?.id === id ? null : state.selectedReservation,
        isLoading: false,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to cancel reservation';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  checkAvailability: async (roomId: number, checkInDate: string, checkOutDate: string) => {
    try {
      const response = await apiClient.checkAvailability(roomId, checkInDate, checkOutDate);
      return response.available;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to check availability';
      set({ error: message });
      return false;
    }
  },

  setSelectedReservation: (reservation: Reservation | null) => set({ selectedReservation: reservation }),
  clearError: () => set({ error: null }),
}));
