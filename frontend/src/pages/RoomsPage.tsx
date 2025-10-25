/**
 * Rooms Management Page
 * Features: Level view (A/B sections), Status filter, View toggle
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import type { Room } from '../services/api';
import { useRoomStore } from '../stores/roomStore';

type ViewMode = 'level' | 'grid';
type StatusFilter = 'all' | 'available' | 'occupied';

export function RoomsPage() {
  const { t } = useTranslation();
  const { rooms, isLoading, fetchRooms, deleteRoom } = useRoomStore();
  const [showForm, setShowForm] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('level'); // Default to level view
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');

  // Helper function to translate status
  const translateStatus = (status: string) => {
    return t(`rooms.${status}`);
  };
  const [formData, setFormData] = useState<Partial<Room>>({
    room_number: '',
    floor: 2,
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
      setError(t('common.requiredFields'));
      return;
    }

    try {
      await useRoomStore.getState().createRoom(formData);
      setFormData({
        room_number: '',
        floor: 2,
        room_type: 'single',
        monthly_rate: 0,
        status: 'available',
        amenities: '',
      });
      setShowForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('rooms.createFailed'));
    }
  };

  const handleDeleteRoom = async (id: number) => {
    if (confirm(t('rooms.confirmDelete'))) {
      try {
        await deleteRoom(id);
      } catch (err) {
        setError(err instanceof Error ? err.message : t('rooms.deleteFailed'));
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

  // Filter rooms by status
  const filteredRooms = rooms.filter(room => {
    if (statusFilter === 'all') return true;
    return room.status === statusFilter;
  });

  // Group rooms by floor (Floor 2 = A/Atas/Upper, Floor 1 = B/Bawah/Lower)
  const roomsLevelA = filteredRooms.filter(room => room.floor === 2);
  const roomsLevelB = filteredRooms.filter(room => room.floor === 1);

  // Room Card Component
  const RoomCard = ({ room }: { room: Room }) => (
    <div key={room.id} className="bg-white rounded-lg shadow hover:shadow-lg transition p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xl font-bold text-gray-900">{room.room_number}</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(room.status)}`}>
          {translateStatus(room.status)}
        </span>
      </div>

      <div className="space-y-1 mb-3 text-sm">
        <p className="text-gray-600">
          <strong>{t('rooms.roomType')}:</strong> {t(`rooms.${room.room_type}`)}
        </p>
        <p className="text-gray-600">
          <strong>{t('rooms.floor')}:</strong> {room.floor}
        </p>
        <p className="text-gray-900 font-semibold">
          Rp {room.monthly_rate.toLocaleString('id-ID')} {t('rooms.perMonth')}
        </p>
        {room.current_tenant && (
          <p className="text-blue-600 text-sm">
            <strong>{t('tenants.title')}:</strong> {room.current_tenant.name}
          </p>
        )}
      </div>

      <div className="flex gap-2">
        <Link
          to={`/rooms/${room.id}`}
          className="flex-1 py-2 px-3 bg-blue-100 hover:bg-blue-200 text-blue-700 font-medium rounded-lg text-sm text-center transition"
        >
          {t('common.view')}
        </Link>
        <button
          onClick={() => handleDeleteRoom(room.id)}
          className="flex-1 py-2 px-3 bg-red-100 hover:bg-red-200 text-red-700 font-medium rounded-lg text-sm transition"
        >
          {t('common.delete')}
        </button>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('rooms.title')}</h1>
          <p className="text-gray-600 mt-1">{t('rooms.subtitle')}</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition"
        >
          {showForm ? `✕ ${t('common.cancel')}` : `+ ${t('rooms.addRoom')}`}
        </button>
      </div>

      {/* Controls: View Toggle + Status Filter */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* View Mode Toggle */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">{t('common.view')}:</span>
            <div className="inline-flex rounded-lg border border-gray-300 bg-gray-50">
              <button
                onClick={() => setViewMode('level')}
                className={`px-4 py-2 text-sm font-medium rounded-l-lg transition ${
                  viewMode === 'level'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {t('rooms.levelView')}
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`px-4 py-2 text-sm font-medium rounded-r-lg transition ${
                  viewMode === 'grid'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {t('rooms.gridView')}
              </button>
            </div>
          </div>

          {/* Status Filter */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">{t('common.filter')}:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
            >
              <option value="all">{t('payments.allPayments')}</option>
              <option value="available">{t('rooms.available')}</option>
              <option value="occupied">{t('rooms.occupied')}</option>
            </select>
          </div>

          {/* Stats */}
          <div className="ml-auto flex gap-4 text-sm">
            <div className="px-3 py-1 bg-green-100 text-green-800 rounded-full font-medium">
              {t('rooms.available')}: {rooms.filter(r => r.status === 'available').length}
            </div>
            <div className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-medium">
              {t('rooms.occupied')}: {rooms.filter(r => r.status === 'occupied').length}
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* Create Room Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">{t('rooms.addRoom')}</h2>
          <form onSubmit={handleCreateRoom} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Room Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('rooms.roomNumber')} *
              </label>
              <input
                type="text"
                name="room_number"
                value={formData.room_number}
                onChange={handleInputChange}
                placeholder={t('rooms.placeholders.roomNumber')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Floor */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('rooms.floor')}
              </label>
              <select
                name="floor"
                value={formData.floor}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value={2}>{t('rooms.floor2Upper')}</option>
                <option value={1}>{t('rooms.floor1Lower')}</option>
              </select>
            </div>

            {/* Room Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('rooms.roomType')}
              </label>
              <select
                name="room_type"
                value={formData.room_type}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="single">{t('rooms.single')}</option>
                <option value="double">{t('rooms.double')}</option>
                <option value="suite">{t('rooms.suite')}</option>
              </select>
            </div>

            {/* Monthly Rate */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('rooms.monthlyRate')} (IDR) *
              </label>
              <input
                type="number"
                name="monthly_rate"
                value={formData.monthly_rate}
                onChange={handleInputChange}
                placeholder={t('rooms.placeholders.monthlyRate')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('common.status')}
              </label>
              <select
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="available">{t('rooms.available')}</option>
                <option value="occupied">{t('rooms.occupied')}</option>
                <option value="maintenance">{t('rooms.maintenance')}</option>
              </select>
            </div>

            {/* Amenities */}
            <div className="md:col-span-2 lg:col-span-3">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('rooms.amenities')}
              </label>
              <input
                type="text"
                name="amenities"
                value={formData.amenities}
                onChange={handleInputChange}
                placeholder={t('rooms.placeholders.amenities')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="md:col-span-2 lg:col-span-3 py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition"
            >
              {isLoading ? t('rooms.creating') : t('rooms.createRoom')}
            </button>
          </form>
        </div>
      )}

      {/* Rooms Display */}
      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">{t('common.loading')}</p>
        </div>
      ) : filteredRooms.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 text-lg">
            {statusFilter === 'all'
              ? t('rooms.noRooms')
              : t('rooms.noRoomsFiltered', { status: t(`rooms.${statusFilter}`) })}
          </p>
        </div>
      ) : viewMode === 'level' ? (
        /* Level View - A (Atas) and B (Bawah) sections */
        <div className="space-y-8">
          {/* Level A - Upper */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-2xl font-bold text-gray-900">{t('rooms.levelAUpper')}</h2>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">
                {roomsLevelA.length} {t('rooms.rooms')}
              </span>
            </div>
            {roomsLevelA.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                {roomsLevelA.map((room) => (
                  <RoomCard key={room.id} room={room} />
                ))}
              </div>
            ) : (
              <div className="bg-gray-50 rounded-lg p-8 text-center">
                <p className="text-gray-500">{t('rooms.noRoomsLevelA')}</p>
              </div>
            )}
          </div>

          {/* Level B - Lower */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-2xl font-bold text-gray-900">{t('rooms.levelBLower')}</h2>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">
                {roomsLevelB.length} {t('rooms.rooms')}
              </span>
            </div>
            {roomsLevelB.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                {roomsLevelB.map((room) => (
                  <RoomCard key={room.id} room={room} />
                ))}
              </div>
            ) : (
              <div className="bg-gray-50 rounded-lg p-8 text-center">
                <p className="text-gray-500">{t('rooms.noRoomsLevelB')}</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Grid View - All rooms in one grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRooms.map((room) => (
            <RoomCard key={room.id} room={room} />
          ))}
        </div>
      )}
    </div>
  );
}
