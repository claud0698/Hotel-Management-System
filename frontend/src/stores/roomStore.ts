/**
 * Room Store
 * Manages room data and operations
 */

import { create } from 'zustand';
import type { Room } from '../services/api';
import { apiClient } from '../services/api';

interface RoomState {
  rooms: Room[];
  selectedRoom: Room | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchRooms: () => Promise<void>;
  fetchRoom: (id: number) => Promise<void>;
  createRoom: (data: Partial<Room>) => Promise<Room>;
  updateRoom: (id: number, data: Partial<Room>) => Promise<Room>;
  deleteRoom: (id: number) => Promise<void>;
  setSelectedRoom: (room: Room | null) => void;
  clearError: () => void;
}

export const useRoomStore = create<RoomState>((set) => ({
  rooms: [],
  selectedRoom: null,
  isLoading: false,
  error: null,

  fetchRooms: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getRooms();
      set({
        rooms: response.rooms || [],
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch rooms';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  fetchRoom: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getRoom(id);
      set({
        selectedRoom: response.room,
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch room';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  createRoom: async (data: Partial<Room>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.createRoom(data);
      set((state) => ({
        rooms: [...state.rooms, response.room],
        isLoading: false,
      }));
      return response.room;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create room';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  updateRoom: async (id: number, data: Partial<Room>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.updateRoom(id, data);
      set((state) => ({
        rooms: state.rooms.map((r) => (r.id === id ? response.room : r)),
        selectedRoom: state.selectedRoom?.id === id ? response.room : state.selectedRoom,
        isLoading: false,
      }));
      return response.room;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update room';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  deleteRoom: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.deleteRoom(id);
      set((state) => ({
        rooms: state.rooms.filter((r) => r.id !== id),
        selectedRoom: state.selectedRoom?.id === id ? null : state.selectedRoom,
        isLoading: false,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete room';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  setSelectedRoom: (room: Room | null) => set({ selectedRoom: room }),
  clearError: () => set({ error: null }),
}));
