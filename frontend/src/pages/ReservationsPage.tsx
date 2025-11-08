/**
 * Reservations Page
 * Manage hotel reservations - create, view, update, check-in/out
 */

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useReservationStore } from '../stores/reservationStore';
import { useGuestStore } from '../stores/guestStore';
import { useRoomStore } from '../stores/roomStore';
import {
  Card,
  Button,
  Input,
  Select,
  Modal,
  Alert,
  Badge,
  Table,
  LoadingSpinner,
  Skeleton,
} from '../components/ui';
import type { Reservation, Guest, Room } from '../services/api';

export function ReservationsPage() {
  const { t } = useTranslation();
  const {
    reservations,
    isLoading,
    error,
    fetchReservations,
    fetchReservation,
    createReservation,
    updateReservation,
    checkInReservation,
    checkOutReservation,
    cancelReservation,
    setSelectedReservation,
    clearError,
  } = useReservationStore();

  const { guests, fetchGuests } = useGuestStore();
  const { rooms, fetchRooms } = useRoomStore();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  const [deletingReservationId, setDeletingReservationId] = useState<number | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [selectedReservationData, setSelectedReservationData] = useState<Reservation | null>(null);

  const [formData, setFormData] = useState({
    guest_id: '',
    room_id: '',
    check_in_date: '',
    check_out_date: '',
    total_amount: '',
    notes: '',
  });

  const [filterStatus, setFilterStatus] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');

  // Load data on mount
  useEffect(() => {
    fetchReservations();
    fetchGuests();
    fetchRooms();
  }, []);

  // Filter and search
  const filteredReservations = reservations.filter((res) => {
    const matchesStatus = !filterStatus || res.status === filterStatus;
    const matchesSearch =
      !searchTerm ||
      res.guest?.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      res.room?.room_number?.includes(searchTerm) ||
      res.id.toString().includes(searchTerm);
    return matchesStatus && matchesSearch;
  });

  const handleOpenModal = (reservation?: Reservation) => {
    if (reservation) {
      setEditingId(reservation.id);
      setFormData({
        guest_id: reservation.guest_id.toString(),
        room_id: reservation.room_id.toString(),
        check_in_date: reservation.check_in_date.split('T')[0],
        check_out_date: reservation.check_out_date.split('T')[0],
        total_amount: reservation.total_amount.toString(),
        notes: reservation.notes || '',
      });
    } else {
      setEditingId(null);
      setFormData({
        guest_id: '',
        room_id: '',
        check_in_date: '',
        check_out_date: '',
        total_amount: '',
        notes: '',
      });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    if (
      !formData.guest_id ||
      !formData.room_id ||
      !formData.check_in_date ||
      !formData.check_out_date ||
      !formData.total_amount
    ) {
      return;
    }

    try {
      const data = {
        guest_id: parseInt(formData.guest_id),
        room_id: parseInt(formData.room_id),
        check_in_date: new Date(formData.check_in_date).toISOString(),
        check_out_date: new Date(formData.check_out_date).toISOString(),
        total_amount: parseFloat(formData.total_amount),
        notes: formData.notes || undefined,
      };

      if (editingId) {
        await updateReservation(editingId, data);
      } else {
        await createReservation(data);
      }

      handleCloseModal();
      await fetchReservations();
    } catch {
      // Error is handled by the store
    }
  };

  const handleCheckIn = async (reservationId: number) => {
    try {
      await checkInReservation(reservationId);
      await fetchReservations();
    } catch {
      // Error is handled by the store
    }
  };

  const handleCheckOut = async (reservationId: number) => {
    try {
      await checkOutReservation(reservationId);
      await fetchReservations();
    } catch {
      // Error is handled by the store
    }
  };

  const handleCancel = async (reservationId: number) => {
    if (confirm('Are you sure you want to cancel this reservation?')) {
      try {
        await cancelReservation(reservationId);
        await fetchReservations();
      } catch {
        // Error is handled by the store
      }
    }
  };

  const handleDeleteClick = (reservationId: number) => {
    setDeletingReservationId(reservationId);
    setIsDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (deletingReservationId) {
      try {
        await cancelReservation(deletingReservationId);
        await fetchReservations();
        setIsDeleteConfirmOpen(false);
        setDeletingReservationId(null);
      } catch {
        // Error is handled by the store
      }
    }
  };

  const handleDeleteCancel = () => {
    setIsDeleteConfirmOpen(false);
    setDeletingReservationId(null);
  };

  const handleViewDetails = async (reservation: Reservation) => {
    setSelectedReservationData(reservation);
    setIsDetailModalOpen(true);
  };

  const getStatusBadge = (status: string) => {
    const variantMap: Record<string, 'default' | 'success' | 'warning' | 'danger' | 'info'> = {
      confirmed: 'info',
      checked_in: 'success',
      checked_out: 'default',
      cancelled: 'danger',
    };
    return <Badge variant={variantMap[status] || 'default'}>{status}</Badge>;
  };

  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      confirmed: 'text-blue-600',
      checked_in: 'text-green-600',
      checked_out: 'text-gray-600',
      cancelled: 'text-red-600',
    };
    return colorMap[status] || 'text-gray-600';
  };

  const columns = [
    {
      key: 'id',
      header: 'ID',
      width: 'w-16',
      render: (value: number) => <span className="font-semibold">#{value}</span>,
    },
    {
      key: 'guest',
      header: 'Guest',
      render: (value: any, row: Reservation) => row.guest?.full_name || 'N/A',
    },
    {
      key: 'room',
      header: 'Room',
      render: (value: any, row: Reservation) => row.room?.room_number || 'N/A',
    },
    {
      key: 'check_in_date',
      header: 'Check-in',
      render: (value: string) => new Date(value).toLocaleDateString(),
    },
    {
      key: 'check_out_date',
      header: 'Check-out',
      render: (value: string) => new Date(value).toLocaleDateString(),
    },
    {
      key: 'total_amount',
      header: 'Amount',
      render: (value: number) =>
        new Intl.NumberFormat('id-ID', {
          style: 'currency',
          currency: 'IDR',
          minimumFractionDigits: 0,
        }).format(value),
    },
    {
      key: 'balance',
      header: 'Balance',
      render: (value: number) =>
        new Intl.NumberFormat('id-ID', {
          style: 'currency',
          currency: 'IDR',
          minimumFractionDigits: 0,
        }).format(value),
    },
    {
      key: 'status',
      header: 'Status',
      render: (value: string) => getStatusBadge(value),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reservations</h1>
          <p className="text-gray-600 mt-1">Manage guest reservations</p>
        </div>
        <Button onClick={() => handleOpenModal()} size="lg">
          + New Reservation
        </Button>
      </div>

      {/* Alerts */}
      {error && (
        <Alert
          type="error"
          title="Error"
          message={error}
          onClose={clearError}
        />
      )}

      {/* Filters */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            placeholder="Search by guest, room, or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <Select
            options={[
              { value: '', label: 'All Statuses' },
              { value: 'confirmed', label: 'Confirmed' },
              { value: 'checked_in', label: 'Checked In' },
              { value: 'checked_out', label: 'Checked Out' },
              { value: 'cancelled', label: 'Cancelled' },
            ]}
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            placeholder="Filter by status"
          />
        </div>
      </Card>

      {/* Table */}
      {isLoading ? (
        <Card>
          <div className="py-8">
            <LoadingSpinner message="Loading reservations..." />
          </div>
        </Card>
      ) : filteredReservations.length === 0 ? (
        <Card>
          <div className="py-8 text-center">
            <p className="text-gray-500">No reservations found</p>
          </div>
        </Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {columns.map((col) => (
                    <th
                      key={col.key}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider"
                    >
                      {col.header}
                    </th>
                  ))}
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredReservations.map((reservation) => (
                  <tr key={reservation.id} className="hover:bg-gray-50">
                    {columns.map((col) => (
                      <td
                        key={`${reservation.id}-${col.key}`}
                        className="px-6 py-4 text-sm text-gray-900"
                      >
                        {col.render
                          ? col.render((reservation as any)[col.key], reservation)
                          : (reservation as any)[col.key]}
                      </td>
                    ))}
                    <td className="px-6 py-4 text-right whitespace-nowrap text-sm font-medium space-x-2">
                      <button
                        onClick={() => handleViewDetails(reservation)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        View
                      </button>
                      {reservation.status === 'confirmed' && (
                        <button
                          onClick={() => handleCheckIn(reservation.id)}
                          className="text-green-600 hover:text-green-800"
                        >
                          Check-in
                        </button>
                      )}
                      {reservation.status === 'checked_in' && (
                        <button
                          onClick={() => handleCheckOut(reservation.id)}
                          className="text-orange-600 hover:text-orange-800"
                        >
                          Check-out
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteClick(reservation.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingId ? 'Edit Reservation' : 'New Reservation'}
        size="lg"
        footer={
          <>
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} isLoading={isLoading}>
              {editingId ? 'Update' : 'Create'} Reservation
            </Button>
          </>
        }
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Select
            label="Guest"
            options={guests.map((g) => ({
              value: g.id,
              label: g.full_name,
            }))}
            value={formData.guest_id}
            onChange={(e) => setFormData({ ...formData, guest_id: e.target.value })}
            required
          />

          <Select
            label="Room"
            options={rooms.map((r) => ({
              value: r.id,
              label: `${r.room_number} (${r.room_type?.name || 'Unknown'})`,
            }))}
            value={formData.room_id}
            onChange={(e) => setFormData({ ...formData, room_id: e.target.value })}
            required
          />

          <Input
            label="Check-in Date"
            type="date"
            value={formData.check_in_date}
            onChange={(e) => setFormData({ ...formData, check_in_date: e.target.value })}
            required
          />

          <Input
            label="Check-out Date"
            type="date"
            value={formData.check_out_date}
            onChange={(e) => setFormData({ ...formData, check_out_date: e.target.value })}
            required
          />

          <Input
            label="Total Amount (IDR)"
            type="number"
            value={formData.total_amount}
            onChange={(e) => setFormData({ ...formData, total_amount: e.target.value })}
            required
          />

          <Input
            label="Notes"
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            placeholder="Optional notes about the reservation"
          />
        </form>
      </Modal>

      {/* Detail Modal */}
      <Modal
        isOpen={isDetailModalOpen}
        onClose={() => setIsDetailModalOpen(false)}
        title="Reservation Details"
        size="lg"
        footer={
          <Button variant="secondary" onClick={() => setIsDetailModalOpen(false)}>
            Close
          </Button>
        }
      >
        {selectedReservationData && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Reservation ID</p>
                <p className="font-semibold">#{selectedReservationData.id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="font-semibold">{getStatusBadge(selectedReservationData.status)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Guest</p>
                <p className="font-semibold">{selectedReservationData.guest?.full_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Room</p>
                <p className="font-semibold">{selectedReservationData.room?.room_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Check-in</p>
                <p className="font-semibold">
                  {new Date(selectedReservationData.check_in_date).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Check-out</p>
                <p className="font-semibold">
                  {new Date(selectedReservationData.check_out_date).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Amount</p>
                <p className="font-semibold">
                  {new Intl.NumberFormat('id-ID', {
                    style: 'currency',
                    currency: 'IDR',
                    minimumFractionDigits: 0,
                  }).format(selectedReservationData.total_amount)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Paid</p>
                <p className="font-semibold">
                  {new Intl.NumberFormat('id-ID', {
                    style: 'currency',
                    currency: 'IDR',
                    minimumFractionDigits: 0,
                  }).format(selectedReservationData.total_paid)}
                </p>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-gray-600">Balance</p>
                <p className={`font-semibold text-lg ${
                  selectedReservationData.balance > 0 ? 'text-red-600' : 'text-green-600'
                }`}>
                  {new Intl.NumberFormat('id-ID', {
                    style: 'currency',
                    currency: 'IDR',
                    minimumFractionDigits: 0,
                  }).format(selectedReservationData.balance)}
                </p>
              </div>
            </div>

            {selectedReservationData.notes && (
              <div className="pt-4 border-t">
                <p className="text-sm text-gray-600 mb-1">Notes</p>
                <p className="text-gray-900">{selectedReservationData.notes}</p>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteConfirmOpen}
        onClose={handleDeleteCancel}
        title={t('reservations.confirmDelete') || 'Delete Reservation'}
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={handleDeleteCancel}>
              {t('common.cancel')}
            </Button>
            <Button variant="danger" onClick={handleDeleteConfirm} isLoading={isLoading}>
              {t('common.delete')}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            {t('reservations.confirmDelete') || 'Are you sure you want to delete this reservation?'}
          </p>
          {deletingReservationId && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-sm text-red-800">
                <strong>Warning:</strong> This action cannot be undone. The reservation will be marked as cancelled in the system.
              </p>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
}
