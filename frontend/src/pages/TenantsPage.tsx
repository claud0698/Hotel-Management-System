/**
 * Tenants Management Page
 */

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Tenant } from '../services/api';
import { useTenantStore } from '../stores/tenantStore';
import { useRoomStore } from '../stores/roomStore';

export function TenantsPage() {
  const { t } = useTranslation();
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

  // Helper function to translate status
  const translateStatus = (status: string) => {
    if (status === 'moved_out') return t('tenants.inactive'); // Map moved_out to inactive translation
    return t(`tenants.${status}`);
  };

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
    if (!roomId) return t('tenants.notAssigned');
    const room = rooms.find((r) => r.id === roomId);
    return room ? `${t('rooms.title')} ${room.room_number}` : t('tenants.notAssigned');
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
          <h1 className="text-3xl font-bold text-gray-900">{t('tenants.title')}</h1>
          <p className="text-gray-600 mt-1">{t('nav.management')}</p>
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
          {showForm ? `✕ ${t('common.cancel')}` : `+ ${t('tenants.addTenant')}`}
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
            {editingId ? t('tenants.editTenant') : t('tenants.addTenant')}
          </h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('tenants.name')} *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder={t('tenants.placeholders.name')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Phone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('tenants.phone')}
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder={t('tenants.placeholders.phone')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('tenants.email')}
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder={t('tenants.placeholders.email')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* ID Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('tenants.idNumber')}
              </label>
              <input
                type="text"
                name="id_number"
                value={formData.id_number}
                onChange={handleInputChange}
                placeholder={t('tenants.placeholders.idNumber')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Move-in Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('tenants.moveInDate')}
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
                {t('tenants.currentRoom')}
              </label>
              <select
                name="current_room_id"
                value={formData.current_room_id || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">{t('tenants.selectRoom')}</option>
                {rooms
                  .filter((r) => r.status === 'available' || r.id === formData.current_room_id)
                  .map((room) => (
                    <option key={room.id} value={room.id}>
                      {t('rooms.title')} {room.room_number} ({t(`rooms.${room.status}`)})
                    </option>
                  ))}
              </select>
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('tenants.status')}
              </label>
              <select
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="active">{t('tenants.active')}</option>
                <option value="inactive">{t('tenants.inactive')}</option>
                <option value="moved_out">{t('tenants.inactive')}</option>
              </select>
            </div>

            {/* Notes */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('tenants.notes')}
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                placeholder={t('tenants.placeholders.notes')}
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
              {isLoading ? (editingId ? t('tenants.updating') : t('tenants.creating')) : editingId ? t('tenants.updateTenant') : t('tenants.createTenant')}
            </button>
          </form>
        </div>
      )}

      {/* Tenants Table */}
      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">{t('common.loading')}</p>
        </div>
      ) : tenants.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 text-lg">{t('tenants.noTenants')}</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('tenants.name')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('tenants.currentRoom')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('tenants.phone')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('tenants.moveInDate')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('tenants.status')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('tenants.actions')}</th>
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
                        {translateStatus(tenant.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm flex gap-2">
                      <button
                        onClick={() => handleEdit(tenant)}
                        className="px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 font-medium rounded text-xs transition"
                      >
                        {t('common.edit')}
                      </button>
                      <button
                        onClick={() => handleDelete(tenant.id)}
                        className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 font-medium rounded text-xs transition"
                      >
                        {t('common.delete')}
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
