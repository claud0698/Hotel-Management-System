/**
 * Tenants Management Page
 */

import { useEffect, useState } from 'react';
import type { Tenant } from '../services/api';
import { useTenantStore } from '../stores/tenantStore';
import { useRoomStore } from '../stores/roomStore';

export function TenantsPage() {
  const { tenants, isLoading, fetchTenants, createTenant, updateTenant, deleteTenant } = useTenantStore();
  const { rooms, fetchRooms } = useRoomStore();
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<Partial<Tenant>>({
    name: '',
    phone: '',
    email: '',
    id_number: '',
    move_in_date: new Date().toISOString().split('T')[0],
    current_room_id: undefined,
    status: 'active',
    notes: '',
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTenants();
    fetchRooms();
  }, []);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'current_room_id' && value ? parseInt(value) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.name || formData.name.trim() === '') {
      setError('Tenant name is required');
      return;
    }

    try {
      if (editingId) {
        await updateTenant(editingId, formData);
      } else {
        await createTenant(formData);
      }

      setFormData({
        name: '',
        phone: '',
        email: '',
        id_number: '',
        move_in_date: new Date().toISOString().split('T')[0],
        current_room_id: undefined,
        status: 'active',
        notes: '',
      });
      setShowForm(false);
      setEditingId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save tenant');
    }
  };

  const handleEdit = (tenant: Tenant) => {
    setFormData(tenant);
    setEditingId(tenant.id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this tenant?')) {
      try {
        await deleteTenant(id);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete tenant');
      }
    }
  };

  const getRoomName = (roomId?: number) => {
    if (!roomId) return 'Not assigned';
    const room = rooms.find((r) => r.id === roomId);
    return room ? `Room ${room.room_number}` : 'Unknown';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'moved_out':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-green-100 text-green-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tenants Management</h1>
          <p className="text-gray-600 mt-1">Manage your tenants</p>
        </div>
        <button
          onClick={() => {
            setEditingId(null);
            setFormData({
              name: '',
              phone: '',
              email: '',
              id_number: '',
              move_in_date: new Date().toISOString().split('T')[0],
              current_room_id: undefined,
              status: 'active',
              notes: '',
            });
            setShowForm(!showForm);
          }}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition"
        >
          {showForm ? '✕ Cancel' : '+ Add Tenant'}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Create/Edit Tenant Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            {editingId ? 'Edit Tenant' : 'Add New Tenant'}
          </h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="e.g., John Doe"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Phone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="e.g., 081234567890"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="e.g., john@example.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* ID Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                ID Number (KTP/Passport)
              </label>
              <input
                type="text"
                name="id_number"
                value={formData.id_number}
                onChange={handleInputChange}
                placeholder="e.g., 1234567890123456"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Move-in Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Move-in Date
              </label>
              <input
                type="date"
                name="move_in_date"
                value={formData.move_in_date?.split('T')[0] || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Room Assignment */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Assign Room
              </label>
              <select
                name="current_room_id"
                value={formData.current_room_id || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a room</option>
                {rooms
                  .filter((r) => r.status === 'available' || r.id === formData.current_room_id)
                  .map((room) => (
                    <option key={room.id} value={room.id}>
                      Room {room.room_number} ({room.status})
                    </option>
                  ))}
              </select>
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
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="moved_out">Moved Out</option>
              </select>
            </div>

            {/* Notes */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                placeholder="Additional information about the tenant..."
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="md:col-span-2 py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition"
            >
              {isLoading ? (editingId ? 'Updating...' : 'Creating...') : editingId ? 'Update Tenant' : 'Create Tenant'}
            </button>
          </form>
        </div>
      )}

      {/* Tenants Table */}
      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading tenants...</p>
        </div>
      ) : tenants.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 text-lg">No tenants yet. Add your first tenant to get started!</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">Room</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">Phone</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">Move-in Date</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {tenants.map((tenant) => (
                  <tr key={tenant.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{tenant.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {getRoomName(tenant.current_room_id)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{tenant.phone || '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {tenant.move_in_date
                        ? new Date(tenant.move_in_date).toLocaleDateString('id-ID')
                        : '-'}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                          tenant.status
                        )}`}
                      >
                        {tenant.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm flex gap-2">
                      <button
                        onClick={() => handleEdit(tenant)}
                        className="px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 font-medium rounded text-xs transition"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(tenant.id)}
                        className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 font-medium rounded text-xs transition"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
