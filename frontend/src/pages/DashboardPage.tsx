/**
 * Dashboard Page
 * Shows key metrics and summary information
 */

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDashboardStore } from '../stores/dashboardStore';

export function DashboardPage() {
  const { t } = useTranslation();
  const { metrics, summary, isLoading, fetchMetrics, fetchSummary } = useDashboardStore();
  const [selectedMonth, setSelectedMonth] = useState('2025-07'); // Default to July 2025 (our seeded data)

  useEffect(() => {
    // Parse selected month and create date range
    const [year, month] = selectedMonth.split('-').map(Number);
    const startDate = new Date(year, month - 1, 1);
    const endDate = new Date(year, month, 1);

    fetchMetrics(startDate.toISOString(), endDate.toISOString());
    fetchSummary();
  }, [selectedMonth]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const getOccupancyColor = (rate: number) => {
    if (rate >= 80) return 'text-green-600';
    if (rate >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (isLoading && !metrics) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-2">⏳</div>
          <p className="text-gray-600">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('dashboard.title')}</h1>
          <p className="text-gray-600 mt-1">{t('common.welcome')}! {t('dashboard.subtitle')}</p>
        </div>

        {/* Month Selector */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">{t('dashboard.month')}:</label>
          <input
            type="month"
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>
      </div>

      {/* Key Metrics Cards */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Occupancy Rate */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">{t('dashboard.occupancyRate')}</p>
                <p className={`text-3xl font-bold mt-2 ${getOccupancyColor(metrics.occupancy_rate)}`}>
                  {Math.round(metrics.occupancy_rate)}%
                </p>
                <p className="text-gray-600 text-xs mt-2">
                  {metrics.occupied_rooms}/{metrics.total_rooms} {t('nav.rooms').toLowerCase()}
                </p>
              </div>
              <div className="text-4xl">🏘️</div>
            </div>
          </div>

          {/* Monthly Revenue */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">{t('dashboard.totalRevenue')}</p>
                <p className="text-2xl font-bold text-green-600 mt-2">
                  {formatCurrency(metrics.total_income)}
                </p>
                <p className="text-gray-600 text-xs mt-2">{t('dashboard.fromPaidRent')}</p>
              </div>
              <div className="text-4xl">💚</div>
            </div>
          </div>

          {/* Monthly Expenses */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">{t('dashboard.totalExpenses')}</p>
                <p className="text-2xl font-bold text-orange-600 mt-2">
                  {formatCurrency(metrics.total_expenses)}
                </p>
                <p className="text-gray-600 text-xs mt-2">{t('dashboard.thisMonth')}</p>
              </div>
              <div className="text-4xl">💸</div>
            </div>
          </div>

          {/* Net Profit */}
          <div className={`rounded-lg shadow p-6 ${metrics.net_profit >= 0 ? 'bg-green-50' : 'bg-red-50'}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">{t('dashboard.netIncome')}</p>
                <p className={`text-2xl font-bold mt-2 ${metrics.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(metrics.net_profit)}
                </p>
                <p className="text-gray-600 text-xs mt-2">{t('dashboard.revenueMinusExpenses')}</p>
              </div>
              <div className="text-4xl">{metrics.net_profit >= 0 ? '📈' : '📉'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Payment Status Summary */}
      {metrics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Payment Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Status</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-yellow-50 rounded">
                <span className="text-yellow-700 font-medium">Pending Payments</span>
                <span className="bg-yellow-200 text-yellow-800 px-3 py-1 rounded-full font-bold">
                  {metrics.pending_count}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-red-50 rounded">
                <div>
                  <span className="text-red-700 font-medium">Overdue Payments</span>
                  <p className="text-red-600 text-sm">{formatCurrency(metrics.overdue_amount)}</p>
                </div>
                <span className="bg-red-200 text-red-800 px-3 py-1 rounded-full font-bold">
                  {metrics.overdue_count}
                </span>
              </div>
            </div>
          </div>

          {/* Room Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Room Status</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded">
                <span className="text-green-700 font-medium">Occupied Rooms</span>
                <span className="bg-green-200 text-green-800 px-3 py-1 rounded-full font-bold">
                  {metrics.occupied_rooms}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded">
                <span className="text-blue-700 font-medium">Available Rooms</span>
                <span className="bg-blue-200 text-blue-800 px-3 py-1 rounded-full font-bold">
                  {metrics.available_rooms}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span className="text-gray-700 font-medium">Total Rooms</span>
                <span className="bg-gray-200 text-gray-800 px-3 py-1 rounded-full font-bold">
                  {metrics.total_rooms}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {summary && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Payments */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('dashboard.recentPayments')}</h3>
            {summary.recent_payments.length > 0 ? (
              <div className="space-y-2">
                {summary.recent_payments.map((payment) => (
                  <div key={payment.id} className="flex items-center justify-between p-2 border-b last:border-b-0">
                    <div>
                      <p className="text-sm font-medium text-gray-900">Payment #{payment.id}</p>
                      <p className="text-xs text-gray-600">
                        {new Date(payment.created_at).toLocaleDateString('id-ID')}
                      </p>
                    </div>
                    <span className={`text-sm font-bold ${
                      payment.status === 'paid' ? 'text-green-600' : 'text-orange-600'
                    }`}>
                      {formatCurrency(payment.amount)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 text-sm">No recent payments</p>
            )}
          </div>

          {/* Recent Expenses */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('dashboard.recentExpenses')}</h3>
            {summary.recent_expenses.length > 0 ? (
              <div className="space-y-2">
                {summary.recent_expenses.map((expense) => (
                  <div key={expense.id} className="flex items-center justify-between p-2 border-b last:border-b-0">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{expense.category}</p>
                      <p className="text-xs text-gray-600">
                        {new Date(expense.date).toLocaleDateString('id-ID')}
                      </p>
                    </div>
                    <span className="text-sm font-bold text-red-600">
                      {formatCurrency(expense.amount)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 text-sm">No recent expenses</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
