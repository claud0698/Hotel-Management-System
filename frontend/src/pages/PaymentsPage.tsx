/**
 * Payments Management Page
 * Track payments for active reservations
 */

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Payment, Reservation, Guest, Room } from '../services/api';
import { apiClient } from '../services/api';
import { formatCurrency } from '../utils/currency';

export function PaymentsPage() {
  const { t } = useTranslation();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [guests, setGuests] = useState<Guest[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    reservation_id: '',
    amount: 0,
    payment_date: new Date().toISOString().split('T')[0],
    payment_method: 'cash',
    reference_number: '',
    notes: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [paymentsRes, reservationsRes, guestsRes, roomsRes] = await Promise.all([
        apiClient.getPayments(),
        apiClient.getReservations(),
        apiClient.getGuests(),
        apiClient.getRooms(),
      ]);

      setPayments(paymentsRes.payments || []);
      setReservations(reservationsRes.reservations || []);
      setGuests(guestsRes.guests || []);
      setRooms(roomsRes.rooms || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('payments.loadFailed'));
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'amount' ? parseFloat(value) : value,
    }));
  };

  const handleCreatePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.reservation_id || formData.amount <= 0) {
      setError(t('payments.selectReservationAndAmount'));
      return;
    }

    try {
      setIsLoading(true);

      await apiClient.createPayment({
        reservation_id: parseInt(formData.reservation_id),
        amount: formData.amount,
        payment_date: formData.payment_date,
        payment_method: formData.payment_method as any,
        payment_type: 'full',
        reference_number: formData.reference_number || undefined,
        notes: formData.notes || undefined,
      });

      // Reload payments and update reservation balances
      const paymentsRes = await apiClient.getPayments();
      setPayments(paymentsRes.payments || []);

      // Reset form
      setFormData({
        reservation_id: '',
        amount: 0,
        payment_date: new Date().toISOString().split('T')[0],
        payment_method: 'cash',
        reference_number: '',
        notes: '',
      });
      setShowForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('payments.createFailed'));
    } finally {
      setIsLoading(false);
    }
  };

  const getGuestName = (reservationId: number) => {
    const reservation = reservations.find((r) => r.id === reservationId);
    if (!reservation || !reservation.guest) return t('common.unknown');
    return reservation.guest.full_name;
  };

  // Helper function to translate status
  const translateStatus = (status: string) => {
    return t(`payments.${status}`);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'overdue':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const filteredPayments = payments.filter((p) => {
    if (filterStatus === 'all') return true;
    return p.status === filterStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('payments.title')}</h1>
          <p className="text-gray-600 mt-1">{t('nav.management')}</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition"
        >
          {showForm ? `✕ ${t('common.cancel')}` : `+ ${t('payments.addPayment')}`}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Create Payment Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('payments.recordPayment')}</h2>
          <form onSubmit={handleCreatePayment} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Reservation Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('reservations.title')} *
              </label>
              <select
                name="reservation_id"
                value={formData.reservation_id}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">{t('reservations.chooseReservation') || 'Select Reservation'}</option>
                {reservations
                  .filter((r) => r.status === 'confirmed' || r.status === 'checked_in')
                  .map((reservation) => (
                    <option key={reservation.id} value={reservation.id}>
                      {reservation.guest?.full_name || 'Unknown'} - Room {reservation.room?.room_number} (Balance: {formatCurrency(reservation.balance)})
                    </option>
                  ))}
              </select>
            </div>

            {/* Payment Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.amount')} (IDR) *
              </label>
              <input
                type="number"
                name="amount"
                value={formData.amount}
                onChange={handleInputChange}
                min="0.01"
                step="1000"
                placeholder="e.g. 500000"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Payment Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.paymentDate')} *
              </label>
              <input
                type="date"
                name="payment_date"
                value={formData.payment_date}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Payment Method */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.paymentMethod')} *
              </label>
              <select
                name="payment_method"
                value={formData.payment_method}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="cash">{t('payments.cash') || 'Cash'}</option>
                <option value="credit_card">{t('payments.creditCard') || 'Credit Card'}</option>
                <option value="debit_card">{t('payments.debitCard') || 'Debit Card'}</option>
                <option value="bank_transfer">{t('payments.bankTransfer') || 'Bank Transfer'}</option>
                <option value="e_wallet">{t('payments.eWallet') || 'E-Wallet'}</option>
                <option value="other">{t('payments.other') || 'Other'}</option>
              </select>
            </div>

            {/* Reference Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.referenceNumber') || 'Reference Number'} ({t('common.optional') || 'Optional'})
              </label>
              <input
                type="text"
                name="reference_number"
                value={formData.reference_number}
                onChange={handleInputChange}
                placeholder="e.g. TRF123456 or RECEIPT-001"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Notes */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.notes')} ({t('common.optional') || 'Optional'})
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                placeholder="Additional notes about this payment"
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="md:col-span-2 py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition"
            >
              {isLoading ? t('payments.recording') : t('payments.recordPayment')}
            </button>
          </form>
        </div>
      )}

      {/* Filter Buttons */}
      <div className="flex gap-2">
        {['all', 'paid', 'pending', 'overdue'].map((status) => (
          <button
            key={status}
            onClick={() => setFilterStatus(status)}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filterStatus === status
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            {status === 'all' ? t('payments.allPayments') : t(`payments.${status}`)}
          </button>
        ))}
      </div>

      {/* Payments Table */}
      {payments.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 text-lg">{t('payments.noPayments')}</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('guests.title') || 'Guest'}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('rooms.title') || 'Room'}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('payments.amount')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('payments.paymentMethod')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('payments.paymentDate')}</th>
                </tr>
              </thead>
              <tbody>
                {filteredPayments.map((payment) => (
                  <tr key={payment.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {payment.reservation?.guest?.full_name || t('common.unknown')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {payment.reservation?.room?.room_number || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                      {formatCurrency(payment.amount)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {payment.payment_method || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {payment.created_at ? new Date(payment.created_at).toLocaleDateString('id-ID') : '-'}
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
