/**
 * Guest Store
 * Manages guest data and operations
 */

import { create } from 'zustand';
import type { Guest } from '../services/api';
import { apiClient } from '../services/api';

interface GuestState {
  guests: Guest[];
  selectedGuest: Guest | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchGuests: () => Promise<void>;
  fetchGuest: (id: number) => Promise<void>;
  createGuest: (data: Partial<Guest>) => Promise<Guest>;
  updateGuest: (id: number, data: Partial<Guest>) => Promise<Guest>;
  deleteGuest: (id: number) => Promise<void>;
  setSelectedGuest: (guest: Guest | null) => void;
  clearError: () => void;
}

export const useGuestStore = create<GuestState>((set) => ({
  guests: [],
  selectedGuest: null,
  isLoading: false,
  error: null,

  fetchGuests: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getGuests();
      set({
        guests: response.guests || [],
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch guests';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  fetchGuest: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getGuest(id);
      set({
        selectedGuest: response.guest,
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch guest';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  createGuest: async (data: Partial<Guest>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.createGuest(data);
      set((state) => ({
        guests: [...state.guests, response.guest],
        isLoading: false,
      }));
      return response.guest;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create guest';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  updateGuest: async (id: number, data: Partial<Guest>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.updateGuest(id, data);
      set((state) => ({
        guests: state.guests.map((g) => (g.id === id ? response.guest : g)),
        selectedGuest: state.selectedGuest?.id === id ? response.guest : state.selectedGuest,
        isLoading: false,
      }));
      return response.guest;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update guest';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  deleteGuest: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.deleteGuest(id);
      set((state) => ({
        guests: state.guests.filter((g) => g.id !== id),
        selectedGuest: state.selectedGuest?.id === id ? null : state.selectedGuest,
        isLoading: false,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete guest';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  setSelectedGuest: (guest: Guest | null) => set({ selectedGuest: guest }),
  clearError: () => set({ error: null }),
}));
