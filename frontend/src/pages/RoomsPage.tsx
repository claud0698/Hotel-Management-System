/**
 * Rooms Management Page
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import type { Room } from '../services/api';
import { useRoomStore } from '../stores/roomStore';

export function RoomsPage() {
  const { rooms, isLoading, fetchRooms, deleteRoom } = useRoomStore();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<Partial<Room>>({
    room_number: '',
    floor: 1,
    room_type: 'single',
    monthly_rate: 0,
    status: 'available',
    amenities: '',
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRooms();
  }, []);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'floor' || name === 'monthly_rate' ? parseFloat(value) : value,
    }));
  };

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.room_number || formData.monthly_rate === undefined || formData.monthly_rate <= 0) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      await useRoomStore.getState().createRoom(formData);
      setFormData({
        room_number: '',
        floor: 1,
        room_type: 'single',
        monthly_rate: 0,
        status: 'available',
        amenities: '',
      });
      setShowForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create room');
    }
  };

  const handleDeleteRoom = async (id: number) => {
    if (confirm('Are you sure you want to delete this room?')) {
      try {
        await deleteRoom(id);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete room');
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'occupied':
        return 'bg-blue-100 text-blue-800';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-green-100 text-green-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Rooms Management</h1>
          <p className="text-gray-600 mt-1">Manage your property rooms</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition"
        >
          {showForm ? '✕ Cancel' : '+ Add Room'}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Create Room Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Add New Room</h2>
          <form onSubmit={handleCreateRoom} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Room Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Room Number *
              </label>
              <input
                type="text"
                name="room_number"
                value={formData.room_number}
                onChange={handleInputChange}
                placeholder="e.g., 101"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Floor */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Floor
              </label>
              <input
                type="number"
                name="floor"
                value={formData.floor}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Room Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Room Type
              </label>
              <select
                name="room_type"
                value={formData.room_type}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="single">Single</option>
                <option value="double">Double</option>
                <option value="suite">Suite</option>
              </select>
            </div>

            {/* Monthly Rate */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Monthly Rate (IDR) *
              </label>
              <input
                type="number"
                name="monthly_rate"
                value={formData.monthly_rate}
                onChange={handleInputChange}
                placeholder="500000"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="available">Available</option>
                <option value="occupied">Occupied</option>
                <option value="maintenance">Maintenance</option>
              </select>
            </div>

            {/* Amenities */}
            <div className="md:col-span-2 lg:col-span-3">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Amenities (comma-separated)
              </label>
              <input
                type="text"
                name="amenities"
                value={formData.amenities}
                onChange={handleInputChange}
                placeholder="e.g., Wi-Fi, Air Conditioner, TV"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="md:col-span-2 lg:col-span-3 py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition"
            >
              {isLoading ? 'Creating...' : 'Create Room'}
            </button>
          </form>
        </div>
      )}

      {/* Rooms Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading rooms...</p>
        </div>
      ) : rooms.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 text-lg">No rooms yet. Create your first room to get started!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {rooms.map((room) => (
            <div key={room.id} className="bg-white rounded-lg shadow hover:shadow-lg transition">
              <div className="p-6">
                {/* Room Number and Status */}
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-2xl font-bold text-gray-900">Room {room.room_number}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(room.status)}`}>
                    {room.status}
                  </span>
                </div>

                {/* Details */}
                <div className="space-y-2 mb-4">
                  <p className="text-gray-600 text-sm">
                    <strong>Type:</strong> {room.room_type}
                  </p>
                  <p className="text-gray-600 text-sm">
                    <strong>Floor:</strong> {room.floor}
                  </p>
                  <p className="text-gray-900 text-sm font-semibold">
                    Rp {room.monthly_rate.toLocaleString('id-ID')} / month
                  </p>
                  {room.amenities && (
                    <p className="text-gray-600 text-xs">
                      <strong>Amenities:</strong> {room.amenities}
                    </p>
                  )}
                  {room.current_tenant && (
                    <p className="text-blue-600 text-sm">
                      <strong>Tenant:</strong> {room.current_tenant.name}
                    </p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Link
                    to={`/rooms/${room.id}`}
                    className="flex-1 py-2 px-3 bg-blue-100 hover:bg-blue-200 text-blue-700 font-medium rounded-lg text-sm text-center transition"
                  >
                    View
                  </Link>
                  <button
                    onClick={() => handleDeleteRoom(room.id)}
                    className="flex-1 py-2 px-3 bg-red-100 hover:bg-red-200 text-red-700 font-medium rounded-lg text-sm transition"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
