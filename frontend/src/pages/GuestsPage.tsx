/**
 * Guests Page
 * Manage hotel guests - create, view, update, delete
 */

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useGuestStore } from '../stores/guestStore';
import {
  Card,
  Button,
  Input,
  Select,
  Modal,
  Alert,
  Badge,
  LoadingSpinner,
} from '../components/ui';
import type { Guest } from '../services/api';

export function GuestsPage() {
  const { t } = useTranslation();
  const {
    guests,
    isLoading,
    error,
    fetchGuests,
    createGuest,
    updateGuest,
    deleteGuest,
    clearError,
  } = useGuestStore();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [selectedGuest, setSelectedGuest] = useState<Guest | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    phone_country_code: '+62',
    id_type: 'passport',
    id_number: '',
    nationality: '',
    birth_date: '',
    is_vip: false,
    notes: '',
  });

  // Load data on mount
  useEffect(() => {
    fetchGuests();
  }, []);

  // Filter guests
  const filteredGuests = guests.filter((guest) => {
    const matchesSearch =
      !searchTerm ||
      guest.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      guest.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      guest.phone?.includes(searchTerm) ||
      guest.id_number.includes(searchTerm);
    return matchesSearch;
  });

  const handleOpenModal = (guest?: Guest) => {
    if (guest) {
      setEditingId(guest.id);
      setFormData({
        full_name: guest.full_name,
        email: guest.email || '',
        phone: guest.phone || '',
        phone_country_code: guest.phone_country_code || '+62',
        id_type: guest.id_type,
        id_number: guest.id_number,
        nationality: guest.nationality || '',
        birth_date: guest.birth_date ? guest.birth_date.split('T')[0] : '',
        is_vip: guest.is_vip,
        notes: guest.notes || '',
      });
    } else {
      setEditingId(null);
      setFormData({
        full_name: '',
        email: '',
        phone: '',
        phone_country_code: '+62',
        id_type: 'passport',
        id_number: '',
        nationality: '',
        birth_date: '',
        is_vip: false,
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

    if (!formData.full_name || !formData.id_type || !formData.id_number) {
      return;
    }

    try {
      const data = {
        full_name: formData.full_name,
        email: formData.email || undefined,
        phone: formData.phone || undefined,
        phone_country_code: formData.phone_country_code,
        id_type: formData.id_type as 'passport' | 'driver_license' | 'national_id' | 'other',
        id_number: formData.id_number,
        nationality: formData.nationality || undefined,
        birth_date: formData.birth_date ? new Date(formData.birth_date).toISOString() : undefined,
        is_vip: formData.is_vip,
        notes: formData.notes || undefined,
      };

      if (editingId) {
        await updateGuest(editingId, data);
      } else {
        await createGuest(data);
      }

      handleCloseModal();
      await fetchGuests();
    } catch {
      // Error is handled by the store
    }
  };

  const handleDelete = async (guestId: number) => {
    if (confirm('Are you sure you want to delete this guest?')) {
      try {
        await deleteGuest(guestId);
        await fetchGuests();
      } catch {
        // Error is handled by the store
      }
    }
  };

  const handleViewDetails = (guest: Guest) => {
    setSelectedGuest(guest);
    setIsDetailModalOpen(true);
  };

  const idTypeOptions = [
    { value: 'passport', label: 'Passport' },
    { value: 'driver_license', label: 'Driver License' },
    { value: 'national_id', label: 'National ID' },
    { value: 'other', label: 'Other' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Guests</h1>
          <p className="text-gray-600 mt-1">Manage guest information and details</p>
        </div>
        <Button onClick={() => handleOpenModal()} size="lg">
          + New Guest
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

      {/* Search */}
      <Card className="p-4">
        <Input
          placeholder="Search by name, email, phone, or ID number..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          icon="🔍"
        />
      </Card>

      {/* Guest List */}
      {isLoading ? (
        <Card>
          <div className="py-8">
            <LoadingSpinner message="Loading guests..." />
          </div>
        </Card>
      ) : filteredGuests.length === 0 ? (
        <Card>
          <div className="py-8 text-center">
            <p className="text-gray-500">No guests found</p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredGuests.map((guest) => (
            <Card key={guest.id} hover onClick={() => handleViewDetails(guest)}>
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {guest.full_name}
                    </h3>
                    {guest.is_vip && (
                      <Badge variant="warning" size="sm" className="mt-1">
                        VIP
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="space-y-1 text-sm text-gray-600">
                  {guest.email && (
                    <div>
                      <span className="font-medium">Email:</span> {guest.email}
                    </div>
                  )}
                  {guest.phone && (
                    <div>
                      <span className="font-medium">Phone:</span> {guest.phone_country_code}{guest.phone}
                    </div>
                  )}
                  <div>
                    <span className="font-medium">ID Type:</span>{' '}
                    {idTypeOptions.find((opt) => opt.value === guest.id_type)?.label}
                  </div>
                  <div>
                    <span className="font-medium">ID Number:</span> {guest.id_number}
                  </div>
                  {guest.nationality && (
                    <div>
                      <span className="font-medium">Nationality:</span> {guest.nationality}
                    </div>
                  )}
                </div>

                <div className="pt-3 border-t flex gap-2">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenModal(guest);
                    }}
                  >
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(guest.id);
                    }}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingId ? 'Edit Guest' : 'New Guest'}
        size="lg"
        footer={
          <>
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} isLoading={isLoading}>
              {editingId ? 'Update' : 'Create'} Guest
            </Button>
          </>
        }
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Full Name *"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            placeholder="Enter guest's full name"
            required
          />

          <div className="grid grid-cols-2 gap-4">
            <Select
              label="ID Type *"
              options={idTypeOptions}
              value={formData.id_type}
              onChange={(e) => setFormData({ ...formData, id_type: e.target.value })}
              required
            />
            <Input
              label="ID Number *"
              value={formData.id_number}
              onChange={(e) => setFormData({ ...formData, id_number: e.target.value })}
              placeholder="e.g., A123456789"
              required
            />
          </div>

          <Input
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder="guest@example.com"
          />

          <div className="grid grid-cols-3 gap-2">
            <Select
              label="Country Code"
              options={[
                { value: '+62', label: '+62 (Indonesia)' },
                { value: '+1', label: '+1 (USA)' },
                { value: '+44', label: '+44 (UK)' },
                { value: '+81', label: '+81 (Japan)' },
              ]}
              value={formData.phone_country_code}
              onChange={(e) => setFormData({ ...formData, phone_country_code: e.target.value })}
            />
            <Input
              label="Phone (Col: 2)"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              placeholder="8123456789"
              containerClassName="col-span-2"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Nationality"
              value={formData.nationality}
              onChange={(e) => setFormData({ ...formData, nationality: e.target.value })}
              placeholder="e.g., Indonesian"
            />
            <Input
              label="Birth Date"
              type="date"
              value={formData.birth_date}
              onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_vip"
              checked={formData.is_vip}
              onChange={(e) => setFormData({ ...formData, is_vip: e.target.checked })}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4 cursor-pointer"
            />
            <label htmlFor="is_vip" className="text-sm font-medium text-gray-700 cursor-pointer">
              Mark as VIP Guest
            </label>
          </div>

          <Input
            label="Notes"
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            placeholder="Additional notes about the guest"
          />
        </form>
      </Modal>

      {/* Detail Modal */}
      <Modal
        isOpen={isDetailModalOpen}
        onClose={() => setIsDetailModalOpen(false)}
        title="Guest Details"
        size="md"
        footer={
          <Button variant="secondary" onClick={() => setIsDetailModalOpen(false)}>
            Close
          </Button>
        }
      >
        {selectedGuest && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-gray-900">{selectedGuest.full_name}</h3>
              {selectedGuest.is_vip && (
                <Badge variant="warning">VIP</Badge>
              )}
            </div>

            <div className="space-y-2 text-sm">
              {selectedGuest.email && (
                <div>
                  <p className="text-gray-600">Email</p>
                  <p className="font-medium">{selectedGuest.email}</p>
                </div>
              )}
              {selectedGuest.phone && (
                <div>
                  <p className="text-gray-600">Phone</p>
                  <p className="font-medium">
                    {selectedGuest.phone_country_code}{selectedGuest.phone}
                  </p>
                </div>
              )}
              <div>
                <p className="text-gray-600">ID Type</p>
                <p className="font-medium">
                  {idTypeOptions.find((opt) => opt.value === selectedGuest.id_type)?.label}
                </p>
              </div>
              <div>
                <p className="text-gray-600">ID Number</p>
                <p className="font-medium">{selectedGuest.id_number}</p>
              </div>
              {selectedGuest.nationality && (
                <div>
                  <p className="text-gray-600">Nationality</p>
                  <p className="font-medium">{selectedGuest.nationality}</p>
                </div>
              )}
              {selectedGuest.birth_date && (
                <div>
                  <p className="text-gray-600">Birth Date</p>
                  <p className="font-medium">
                    {new Date(selectedGuest.birth_date).toLocaleDateString()}
                  </p>
                </div>
              )}
              {selectedGuest.notes && (
                <div>
                  <p className="text-gray-600">Notes</p>
                  <p className="font-medium">{selectedGuest.notes}</p>
                </div>
              )}
            </div>

            <div className="pt-4 border-t flex gap-2">
              <Button
                variant="secondary"
                fullWidth
                onClick={() => {
                  setIsDetailModalOpen(false);
                  handleOpenModal(selectedGuest);
                }}
              >
                Edit
              </Button>
              <Button
                variant="danger"
                fullWidth
                onClick={() => {
                  setIsDetailModalOpen(false);
                  handleDelete(selectedGuest.id);
                }}
              >
                Delete
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
