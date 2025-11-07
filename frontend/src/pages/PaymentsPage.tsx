/**
 * Payments Management Page
 * Simplified for manual payment entry with duration tracking
 */

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Payment, Tenant, Room } from '../services/api';
import { apiClient } from '../services/api';

export function PaymentsPage() {
  const { t } = useTranslation();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    tenant_id: '',
    months: 1,
    payment_date: new Date().toISOString().split('T')[0],
    payment_method: 'cash',
    notes: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [paymentsRes, tenantsRes, roomsRes] = await Promise.all([
        apiClient.getPayments(),
        apiClient.getTenants(),
        apiClient.getRooms(),
      ]);

      setPayments(paymentsRes.payments || []);
      setTenants(tenantsRes.tenants || []);
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
      [name]: name === 'months' ? parseInt(value) : value,
    }));
  };

  const handleCreatePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.tenant_id || formData.months <= 0) {
      setError(t('payments.selectTenantAndMonths'));
      return;
    }

    try {
      setIsLoading(true);

      const tenant = tenants.find((t) => t.id === parseInt(formData.tenant_id));
      const room = rooms.find((r) => r.id === tenant?.current_room_id);

      if (!room) {
        throw new Error(t('payments.tenantNotAssignedToRoom'));
      }

      // Create payment record for each month
      const baseDate = new Date(formData.payment_date);

      for (let i = 0; i < formData.months; i++) {
        const dueDate = new Date(baseDate);
        dueDate.setMonth(dueDate.getMonth() + i);

        await apiClient.createPayment({
          tenant_id: parseInt(formData.tenant_id),
          amount: room.monthly_rate,
          due_date: dueDate.toISOString(),
          status: 'paid',
          paid_date: new Date(formData.payment_date).toISOString(),
          payment_method: formData.payment_method,
          notes: `${t('payments.monthsPaymentNote', { months: formData.months })} - ${formData.notes || ''}`,
        });
      }

      // Reload payments
      const paymentsRes = await apiClient.getPayments();
      setPayments(paymentsRes.payments || []);

      // Reset form
      setFormData({
        tenant_id: '',
        months: 1,
        payment_date: new Date().toISOString().split('T')[0],
        payment_method: 'cash',
        notes: '',
      });
      setShowForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('payments.createFailed'));
    } finally {
      setIsLoading(false);
    }
  };

  const getTenantName = (tenantId: number) => {
    return tenants.find((t) => t.id === tenantId)?.name || t('common.unknown');
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

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

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
            {/* Tenant Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.tenant')} *
              </label>
              <select
                name="tenant_id"
                value={formData.tenant_id}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">{t('payments.chooseTenant')}</option>
                {tenants
                  .filter((t) => t.status === 'active')
                  .map((tenant) => {
                    const room = rooms.find((r) => r.id === tenant.current_room_id);
                    return (
                      <option key={tenant.id} value={tenant.id}>
                        {tenant.name} - {room ? `${t('rooms.title')} ${room.room_number}` : t('payments.noRoom')} (Rp{room?.monthly_rate.toLocaleString('id-ID') || 0})
                      </option>
                    );
                  })}
              </select>
            </div>

            {/* Number of Months */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.numberOfMonths')} *
              </label>
              <input
                type="number"
                name="months"
                value={formData.months}
                onChange={handleInputChange}
                min="1"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">{t('payments.monthsHelp')}</p>
            </div>

            {/* Payment Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.paymentDate')}
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
                {t('payments.paymentMethod')}
              </label>
              <select
                name="payment_method"
                value={formData.payment_method}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="cash">{t('payments.cash')}</option>
                <option value="transfer">{t('payments.bankTransfer')}</option>
                <option value="check">{t('payments.check')}</option>
                <option value="other">{t('payments.other')}</option>
              </select>
            </div>

            {/* Notes */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.notes')} ({t('tenants.optional')})
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                placeholder={t('tenants.placeholders.notes')}
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
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('payments.tenant')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('payments.amount')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('payments.dueDate')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('payments.status')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('payments.paymentMethod')}</th>
                </tr>
              </thead>
              <tbody>
                {filteredPayments.map((payment) => (
                  <tr key={payment.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {getTenantName(payment.tenant_id)}
                    </td>
                    <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                      {formatCurrency(payment.amount)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(payment.due_date).toLocaleDateString('id-ID')}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                          payment.status
                        )}`}
                      >
                        {translateStatus(payment.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {payment.payment_method || '-'}
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
