/**
 * Expenses Management Page
 */

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Expense } from '../services/api';
import { apiClient } from '../services/api';

export function ExpensesPage() {
  const { t } = useTranslation();
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<Expense>>({
    date: new Date().toISOString().split('T')[0],
    category: 'utilities',
    amount: 0,
    description: '',
    receipt_url: '',
  });

  // Helper function to translate category
  const translateCategory = (category: string) => {
    return t(`expenses.${category}`);
  };

  const expenseCategories = [
    { value: 'utilities', emoji: '⚡' },
    { value: 'maintenance', emoji: '🔧' },
    { value: 'supplies', emoji: '📦' },
    { value: 'cleaning', emoji: '🧹' },
    { value: 'other', emoji: '📌' },
  ];

  useEffect(() => {
    loadExpenses();
  }, []);

  const loadExpenses = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.getExpenses();
      setExpenses(response.expenses || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('expenses.loadFailed'));
    } finally {
      setIsLoading(false);
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.date || !formData.category || !formData.amount || formData.amount <= 0) {
      setError(t('common.requiredFields'));
      return;
    }

    try {
      setIsLoading(true);

      if (editingId) {
        await apiClient.updateExpense(editingId, formData);
      } else {
        await apiClient.createExpense(formData);
      }

      await loadExpenses();

      setFormData({
        date: new Date().toISOString().split('T')[0],
        category: 'utilities',
        amount: 0,
        description: '',
        receipt_url: '',
      });
      setShowForm(false);
      setEditingId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('expenses.saveFailed'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (expense: Expense) => {
    setFormData({
      ...expense,
      date: expense.date.split('T')[0],
    });
    setEditingId(expense.id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm(t('expenses.confirmDeleteExpense'))) {
      try {
        setIsLoading(true);
        await apiClient.deleteExpense(id);
        await loadExpenses();
      } catch (err) {
        setError(err instanceof Error ? err.message : t('expenses.deleteFailed'));
      } finally {
        setIsLoading(false);
      }
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const getCategoryLabel = (category: string) => {
    const cat = expenseCategories.find((c) => c.value === category);
    return cat ? `${cat.emoji} ${translateCategory(category)}` : category;
  };

  const totalExpenses = expenses.reduce((sum, exp) => sum + exp.amount, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('expenses.title')}</h1>
          <p className="text-gray-600 mt-1">{t('nav.management')}</p>
        </div>
        <button
          onClick={() => {
            setEditingId(null);
            setFormData({
              date: new Date().toISOString().split('T')[0],
              category: 'utilities',
              amount: 0,
              description: '',
              receipt_url: '',
            });
            setShowForm(!showForm);
          }}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition"
        >
          {showForm ? `✕ ${t('common.cancel')}` : `+ ${t('expenses.addExpense')}`}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Create/Edit Expense Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            {editingId ? t('expenses.updateExpense') : t('expenses.addExpense')}
          </h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('expenses.date')} *
              </label>
              <input
                type="date"
                name="date"
                value={formData.date?.split('T')[0] || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('expenses.category')} *
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {expenseCategories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.emoji} {translateCategory(cat.value)}
                  </option>
                ))}
              </select>
            </div>

            {/* Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('expenses.amount')} (IDR) *
              </label>
              <input
                type="number"
                name="amount"
                value={formData.amount}
                onChange={handleInputChange}
                placeholder={t('expenses.placeholders.amount')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Receipt URL */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('expenses.receiptUrl')} ({t('tenants.optional')})
              </label>
              <input
                type="url"
                name="receipt_url"
                value={formData.receipt_url}
                onChange={handleInputChange}
                placeholder={t('expenses.placeholders.receiptUrl')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Description */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('expenses.description')}
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder={t('expenses.placeholders.description')}
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
              {isLoading ? (editingId ? t('expenses.updating') : t('expenses.creating')) : editingId ? t('expenses.updateExpense') : t('expenses.createExpense')}
            </button>
          </form>
        </div>
      )}

      {/* Total Expenses Card */}
      {expenses.length > 0 && (
        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg shadow p-6 border-l-4 border-orange-600">
          <p className="text-orange-700 text-sm font-medium">{t('dashboard.totalExpenses')}</p>
          <p className="text-3xl font-bold text-orange-600 mt-2">
            {formatCurrency(totalExpenses)}
          </p>
        </div>
      )}

      {/* Expenses Table */}
      {isLoading && expenses.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600">{t('common.loading')}</p>
        </div>
      ) : expenses.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 text-lg">{t('expenses.noExpenses')}</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('expenses.date')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('expenses.category')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('expenses.amount')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('expenses.description')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">{t('expenses.actions')}</th>
                </tr>
              </thead>
              <tbody>
                {expenses.map((expense) => (
                  <tr key={expense.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {new Date(expense.date).toLocaleDateString('id-ID')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {getCategoryLabel(expense.category)}
                    </td>
                    <td className="px-6 py-4 text-sm font-semibold text-red-600">
                      {formatCurrency(expense.amount)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {expense.description || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm flex gap-2">
                      <button
                        onClick={() => handleEdit(expense)}
                        className="px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 font-medium rounded text-xs transition"
                      >
                        {t('common.edit')}
                      </button>
                      <button
                        onClick={() => handleDelete(expense.id)}
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
