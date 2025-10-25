/**
 * Room Detail Page
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useRoomStore } from '../stores/roomStore';
import type { Room } from '../services/api';

export function RoomDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { rooms, fetchRooms, updateRoom, deleteRoom, isLoading } = useRoomStore();
  const [room, setRoom] = useState<Room | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<Partial<Room>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (rooms.length === 0) {
      fetchRooms();
    }
  }, []);

  useEffect(() => {
    if (id && rooms.length > 0) {
      const foundRoom = rooms.find((r) => r.id === parseInt(id));
      if (foundRoom) {
        setRoom(foundRoom);
        setFormData(foundRoom);
      }
    }
  }, [id, rooms]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'floor' || name === 'monthly_rate' ? parseFloat(value) : value,
    }));
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!id) return;

    try {
      await updateRoom(parseInt(id), formData);
      setIsEditing(false);
      // Refresh room data
      await fetchRooms();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update room');
    }
  };

  const handleDelete = async () => {
    if (!id) return;

    if (confirm('Are you sure you want to delete this room? This action cannot be undone.')) {
      try {
        await deleteRoom(parseInt(id));
        navigate('/rooms');
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

  if (isLoading || !room) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Loading room details...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            to="/rooms"
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            ← Back to Rooms
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Room {room.room_number}</h1>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition"
          >
            {isEditing ? 'Cancel Edit' : 'Edit Room'}
          </button>
          <button
            onClick={handleDelete}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition"
          >
            Delete Room
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* Room Details / Edit Form */}
      <div className="bg-white rounded-lg shadow-lg p-8">
        {isEditing ? (
          <form onSubmit={handleUpdate} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Floor */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Floor
                </label>
                <select
                  name="floor"
                  value={formData.floor}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value={2}>Floor 2 (A - Upper)</option>
                  <option value={1}>Floor 1 (B - Lower)</option>
                </select>
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
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Amenities (comma-separated)
                </label>
                <input
                  type="text"
                  name="amenities"
                  value={formData.amenities}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition"
              >
                Save Changes
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsEditing(false);
                  setFormData(room);
                }}
                className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-lg transition"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-6">
            {/* Status Badge */}
            <div>
              <span className={`px-4 py-2 rounded-full text-sm font-semibold ${getStatusColor(room.status)}`}>
                {room.status}
              </span>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-medium text-gray-500">Room Number</h3>
                <p className="text-2xl font-bold text-gray-900 mt-1">{room.room_number}</p>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-500">Floor</h3>
                <p className="text-2xl font-bold text-gray-900 mt-1">{room.floor}</p>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-500">Room Type</h3>
                <p className="text-2xl font-bold text-gray-900 mt-1 capitalize">{room.room_type}</p>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-500">Monthly Rate</h3>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  Rp {room.monthly_rate.toLocaleString('id-ID')}
                </p>
              </div>

              {room.amenities && (
                <div className="md:col-span-2">
                  <h3 className="text-sm font-medium text-gray-500">Amenities</h3>
                  <p className="text-lg text-gray-900 mt-1">{room.amenities}</p>
                </div>
              )}

              {room.current_tenant && (
                <div className="md:col-span-2">
                  <h3 className="text-sm font-medium text-gray-500">Current Tenant</h3>
                  <div className="mt-2 p-4 bg-blue-50 rounded-lg">
                    <p className="text-lg font-semibold text-blue-900">{room.current_tenant.name}</p>
                    <p className="text-sm text-blue-700 mt-1">{room.current_tenant.phone}</p>
                    {room.current_tenant.email && (
                      <p className="text-sm text-blue-700">{room.current_tenant.email}</p>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Metadata */}
            <div className="border-t pt-6 mt-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Metadata</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                <div>
                  <strong>Created:</strong> {new Date(room.created_at).toLocaleString()}
                </div>
                <div>
                  <strong>Last Updated:</strong> {new Date(room.updated_at).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
