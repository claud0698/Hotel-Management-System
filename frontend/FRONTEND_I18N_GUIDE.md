# Frontend i18n (Internationalization) Implementation Guide

**Language Support:** English (en) & Indonesian (id)

---

## 📌 Quick Summary

The frontend needs to support both **English** and **Indonesian** languages for all UI text. This guide provides:
- Complete translation files structure
- Implementation patterns
- Code examples
- Integration checklist

---

## 🗂️ File Structure

```
frontend/
├── src/
│   ├── locales/
│   │   ├── en.json          # English translations
│   │   ├── id.json          # Indonesian translations
│   │   └── index.ts         # i18n configuration & setup
│   ├── hooks/
│   │   ├── useLanguage.ts   # Custom hook for language switching
│   │   └── useTranslation.ts # Custom hook for getting translations
│   ├── context/
│   │   └── LanguageContext.tsx # Language provider/context
│   ├── components/
│   │   ├── LanguageSwitcher.tsx # Language toggle component
│   │   └── ...
│   └── App.tsx
```

---

## 🔧 Implementation Options

### Option 1: Using `i18next` (Recommended for Production)

**Install dependencies:**
```bash
npm install i18next react-i18next i18next-browser-languagedetector i18next-http-backend
```

**File: `src/locales/i18n.ts`**
```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import enTranslations from './en.json';
import idTranslations from './id.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    defaultNS: 'translation',
    ns: ['translation'],
    resources: {
      en: { translation: enTranslations },
      id: { translation: idTranslations },
    },
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });

export default i18n;
```

**File: `src/main.tsx` or `src/index.tsx`**
```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './locales/i18n'; // Import i18n configuration

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

**Usage in components:**
```typescript
import { useTranslation } from 'react-i18next';

export const GuestForm = () => {
  const { t, i18n } = useTranslation();

  return (
    <form>
      <label>{t('form.fullName')}</label>
      <input placeholder={t('form.fullNamePlaceholder')} />

      <label>{t('form.idType')}</label>
      <select>
        <option value="passport">{t('idTypes.passport')}</option>
        <option value="driver_license">{t('idTypes.driverLicense')}</option>
      </select>

      <button>{t('buttons.submit')}</button>

      {/* Language Switcher */}
      <select value={i18n.language} onChange={(e) => i18n.changeLanguage(e.target.value)}>
        <option value="en">English</option>
        <option value="id">Bahasa Indonesia</option>
      </select>
    </form>
  );
};
```

---

### Option 2: Custom Context Hook (Lightweight Alternative)

**File: `src/context/LanguageContext.tsx`**
```typescript
import React, { createContext, useContext, useState, useEffect } from 'react';
import en from '../locales/en.json';
import id from '../locales/id.json';

type LanguageType = 'en' | 'id';

interface LanguageContextType {
  language: LanguageType;
  setLanguage: (lang: LanguageType) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const translations: Record<LanguageType, any> = { en, id };

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<LanguageType>('en');

  // Load language from localStorage
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language') as LanguageType;
    if (savedLanguage && ['en', 'id'].includes(savedLanguage)) {
      setLanguage(savedLanguage);
    }
  }, []);

  // Save to localStorage when changed
  const changeLanguage = (lang: LanguageType) => {
    setLanguage(lang);
    localStorage.setItem('language', lang);
  };

  // Get translation by dot-notation key
  const t = (key: string): string => {
    const keys = key.split('.');
    let value: any = translations[language];

    for (const k of keys) {
      value = value?.[k];
    }

    return value || key; // Return key if translation not found
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage: changeLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};
```

**Usage in components:**
```typescript
import { useLanguage } from '../context/LanguageContext';

export const GuestForm = () => {
  const { t, language, setLanguage } = useLanguage();

  return (
    <form>
      <label>{t('form.fullName')}</label>
      <input />

      <button>{t('buttons.submit')}</button>

      <select value={language} onChange={(e) => setLanguage(e.target.value as 'en' | 'id')}>
        <option value="en">English</option>
        <option value="id">Bahasa Indonesia</option>
      </select>
    </form>
  );
};
```

---

## 📄 Translation Files

### File: `src/locales/en.json`

```json
{
  "common": {
    "appName": "Hotel Management System",
    "language": "Language",
    "english": "English",
    "indonesian": "Bahasa Indonesia",
    "loading": "Loading...",
    "error": "Error",
    "success": "Success",
    "warning": "Warning",
    "confirm": "Are you sure?",
    "close": "Close",
    "cancel": "Cancel"
  },

  "navigation": {
    "dashboard": "Dashboard",
    "guests": "Guests",
    "rooms": "Rooms",
    "reservations": "Reservations",
    "payments": "Payments",
    "settings": "Settings",
    "logout": "Logout"
  },

  "form": {
    "fullName": "Full Name",
    "fullNamePlaceholder": "Enter guest's full name",
    "idType": "ID Type",
    "idTypePlaceholder": "Select ID type",
    "idNumber": "ID Number",
    "idNumberPlaceholder": "Enter ID document number",
    "email": "Email Address",
    "emailPlaceholder": "guest@example.com",
    "phone": "Phone Number",
    "phonePlaceholder": "+1-555-0123",
    "countryCode": "Country Code",
    "countryCodePlaceholder": "e.g., +1, +62",
    "nationality": "Nationality",
    "nationalityPlaceholder": "Select country",
    "dateOfBirth": "Date of Birth",
    "dateOfBirthPlaceholder": "YYYY-MM-DD",
    "vipStatus": "VIP Status",
    "preferredRoomType": "Preferred Room Type",
    "specialRequests": "Special Requests / Notes",
    "specialRequestsPlaceholder": "E.g., high floor, non-smoking, allergies...",
    "requiredField": "This field is required",
    "optionalField": "Optional",
    "requiredInformation": "Required Information",
    "additionalInformation": "Additional Information"
  },

  "idTypes": {
    "passport": "Passport",
    "driverLicense": "Driver License",
    "nationalId": "National ID",
    "visa": "Visa",
    "travelDocument": "Travel Document",
    "other": "Other"
  },

  "roomTypes": {
    "single": "Single Room",
    "double": "Double Room",
    "suite": "Suite",
    "deluxeSuite": "Deluxe Suite"
  },

  "photoTypes": {
    "idPhoto": "ID Photo",
    "passportPhoto": "Passport Photo",
    "licensePhoto": "License Photo",
    "visaPhoto": "Visa Photo"
  },

  "buttons": {
    "submit": "Create Guest",
    "save": "Save",
    "update": "Update",
    "delete": "Delete",
    "cancel": "Cancel",
    "close": "Close",
    "uploadPhoto": "Upload ID Photo",
    "viewPhotos": "View Photos",
    "deletePhoto": "Delete Photo",
    "downloadPhoto": "Download",
    "takePicture": "Take Picture",
    "selectFile": "Select File",
    "back": "Back",
    "next": "Next",
    "previous": "Previous",
    "search": "Search",
    "filter": "Filter",
    "reset": "Reset",
    "export": "Export",
    "import": "Import"
  },

  "messages": {
    "guestCreated": "Guest created successfully",
    "guestUpdated": "Guest updated successfully",
    "guestDeleted": "Guest deleted successfully",
    "photoUploadSuccess": "Photo uploaded successfully",
    "photoDeleteSuccess": "Photo deleted successfully",
    "photoUploadError": "Failed to upload photo",
    "photoDeleteError": "Failed to delete photo",
    "invalidEmail": "Please enter a valid email address",
    "invalidPhone": "Please enter a valid phone number",
    "invalidDate": "Please enter a valid date",
    "emailAlreadyExists": "This email is already registered",
    "fieldRequired": "This field is required",
    "minLength": "Must be at least {{count}} characters",
    "maxLength": "Cannot exceed {{count}} characters",
    "selectOption": "Please select an option",
    "confirmDelete": "Are you sure you want to delete this guest?",
    "confirmDeletePhoto": "Are you sure you want to delete this photo?",
    "noPhotos": "No photos uploaded yet",
    "uploadingPhoto": "Uploading photo...",
    "deletingPhoto": "Deleting photo...",
    "networkError": "Network error. Please try again",
    "serverError": "Server error. Please try again",
    "unexpectedError": "An unexpected error occurred",
    "loading": "Loading...",
    "noResults": "No results found",
    "tryAgain": "Try again"
  },

  "validation": {
    "fullNameMin": "Full name must be at least 2 characters",
    "fullNameMax": "Full name cannot exceed 100 characters",
    "idNumberRequired": "ID number is required",
    "invalidEmailFormat": "Invalid email format",
    "invalidPhoneFormat": "Invalid phone format",
    "invalidDateFormat": "Please use YYYY-MM-DD format",
    "maxFileSize": "File size must not exceed 5MB",
    "invalidFileType": "Invalid file type. Allowed: JPEG, PNG, PDF"
  },

  "sections": {
    "guestInfo": "Guest Information",
    "contactInfo": "Contact Information",
    "identificationInfo": "Identification Information",
    "personalInfo": "Personal Information",
    "preferences": "Preferences",
    "idPhotos": "ID Photos",
    "reservations": "Reservations",
    "paymentHistory": "Payment History"
  },

  "labels": {
    "createdAt": "Created",
    "updatedAt": "Updated",
    "uploadedBy": "Uploaded by",
    "status": "Status",
    "active": "Active",
    "inactive": "Inactive",
    "vip": "VIP",
    "regular": "Regular",
    "total": "Total",
    "results": "Results",
    "showing": "Showing",
    "of": "of",
    "page": "Page",
    "perPage": "Per page",
    "search": "Search guests..."
  },

  "placeholders": {
    "searchGuests": "Search by name or email...",
    "selectOption": "Select an option...",
    "noData": "No data available"
  }
}
```

### File: `src/locales/id.json`

```json
{
  "common": {
    "appName": "Sistem Manajemen Hotel",
    "language": "Bahasa",
    "english": "English",
    "indonesian": "Bahasa Indonesia",
    "loading": "Memuat...",
    "error": "Kesalahan",
    "success": "Berhasil",
    "warning": "Peringatan",
    "confirm": "Anda yakin?",
    "close": "Tutup",
    "cancel": "Batal"
  },

  "navigation": {
    "dashboard": "Dasbor",
    "guests": "Tamu",
    "rooms": "Kamar",
    "reservations": "Reservasi",
    "payments": "Pembayaran",
    "settings": "Pengaturan",
    "logout": "Keluar"
  },

  "form": {
    "fullName": "Nama Lengkap",
    "fullNamePlaceholder": "Masukkan nama lengkap tamu",
    "idType": "Tipe ID",
    "idTypePlaceholder": "Pilih tipe ID",
    "idNumber": "Nomor ID",
    "idNumberPlaceholder": "Masukkan nomor dokumen ID",
    "email": "Alamat Email",
    "emailPlaceholder": "tamu@example.com",
    "phone": "Nomor Telepon",
    "phonePlaceholder": "+62-812-3456-7890",
    "countryCode": "Kode Negara",
    "countryCodePlaceholder": "cth: +62, +1",
    "nationality": "Kewarganegaraan",
    "nationalityPlaceholder": "Pilih negara",
    "dateOfBirth": "Tanggal Lahir",
    "dateOfBirthPlaceholder": "YYYY-MM-DD",
    "vipStatus": "Status VIP",
    "preferredRoomType": "Tipe Kamar Pilihan",
    "specialRequests": "Permintaan Khusus / Catatan",
    "specialRequestsPlaceholder": "Cth: lantai tinggi, bebas asap, alergi...",
    "requiredField": "Bidang ini wajib diisi",
    "optionalField": "Opsional",
    "requiredInformation": "Informasi Wajib",
    "additionalInformation": "Informasi Tambahan"
  },

  "idTypes": {
    "passport": "Paspor",
    "driverLicense": "SIM",
    "nationalId": "KTP",
    "visa": "Visa",
    "travelDocument": "Dokumen Perjalanan",
    "other": "Lainnya"
  },

  "roomTypes": {
    "single": "Kamar Single",
    "double": "Kamar Double",
    "suite": "Suite",
    "deluxeSuite": "Suite Mewah"
  },

  "photoTypes": {
    "idPhoto": "Foto ID",
    "passportPhoto": "Foto Paspor",
    "licensePhoto": "Foto SIM",
    "visaPhoto": "Foto Visa"
  },

  "buttons": {
    "submit": "Buat Tamu",
    "save": "Simpan",
    "update": "Perbarui",
    "delete": "Hapus",
    "cancel": "Batal",
    "close": "Tutup",
    "uploadPhoto": "Unggah Foto ID",
    "viewPhotos": "Lihat Foto",
    "deletePhoto": "Hapus Foto",
    "downloadPhoto": "Unduh",
    "takePicture": "Ambil Foto",
    "selectFile": "Pilih File",
    "back": "Kembali",
    "next": "Selanjutnya",
    "previous": "Sebelumnya",
    "search": "Cari",
    "filter": "Filter",
    "reset": "Atur Ulang",
    "export": "Ekspor",
    "import": "Impor"
  },

  "messages": {
    "guestCreated": "Tamu berhasil dibuat",
    "guestUpdated": "Tamu berhasil diperbarui",
    "guestDeleted": "Tamu berhasil dihapus",
    "photoUploadSuccess": "Foto berhasil diunggah",
    "photoDeleteSuccess": "Foto berhasil dihapus",
    "photoUploadError": "Gagal mengunggah foto",
    "photoDeleteError": "Gagal menghapus foto",
    "invalidEmail": "Masukkan alamat email yang valid",
    "invalidPhone": "Masukkan nomor telepon yang valid",
    "invalidDate": "Masukkan tanggal yang valid",
    "emailAlreadyExists": "Email ini sudah terdaftar",
    "fieldRequired": "Bidang ini wajib diisi",
    "minLength": "Minimal {{count}} karakter",
    "maxLength": "Maksimal {{count}} karakter",
    "selectOption": "Silakan pilih opsi",
    "confirmDelete": "Anda yakin ingin menghapus tamu ini?",
    "confirmDeletePhoto": "Anda yakin ingin menghapus foto ini?",
    "noPhotos": "Belum ada foto yang diunggah",
    "uploadingPhoto": "Mengunggah foto...",
    "deletingPhoto": "Menghapus foto...",
    "networkError": "Kesalahan jaringan. Silakan coba lagi",
    "serverError": "Kesalahan server. Silakan coba lagi",
    "unexpectedError": "Terjadi kesalahan yang tidak terduga",
    "loading": "Memuat...",
    "noResults": "Tidak ada hasil ditemukan",
    "tryAgain": "Coba lagi"
  },

  "validation": {
    "fullNameMin": "Nama lengkap minimal 2 karakter",
    "fullNameMax": "Nama lengkap maksimal 100 karakter",
    "idNumberRequired": "Nomor ID wajib diisi",
    "invalidEmailFormat": "Format email tidak valid",
    "invalidPhoneFormat": "Format telepon tidak valid",
    "invalidDateFormat": "Gunakan format YYYY-MM-DD",
    "maxFileSize": "Ukuran file tidak boleh lebih dari 5MB",
    "invalidFileType": "Tipe file tidak valid. Yang diizinkan: JPEG, PNG, PDF"
  },

  "sections": {
    "guestInfo": "Informasi Tamu",
    "contactInfo": "Informasi Kontak",
    "identificationInfo": "Informasi Identitas",
    "personalInfo": "Informasi Pribadi",
    "preferences": "Preferensi",
    "idPhotos": "Foto ID",
    "reservations": "Reservasi",
    "paymentHistory": "Riwayat Pembayaran"
  },

  "labels": {
    "createdAt": "Dibuat",
    "updatedAt": "Diperbarui",
    "uploadedBy": "Diunggah oleh",
    "status": "Status",
    "active": "Aktif",
    "inactive": "Tidak Aktif",
    "vip": "VIP",
    "regular": "Reguler",
    "total": "Total",
    "results": "Hasil",
    "showing": "Menampilkan",
    "of": "dari",
    "page": "Halaman",
    "perPage": "Per halaman",
    "search": "Cari tamu..."
  },

  "placeholders": {
    "searchGuests": "Cari berdasarkan nama atau email...",
    "selectOption": "Pilih opsi...",
    "noData": "Tidak ada data"
  }
}
```

---

## 🔌 Component Examples

### Language Switcher Component

```typescript
import { useLanguage } from '../context/LanguageContext';
// OR for i18next:
// import { useTranslation } from 'react-i18next';

export const LanguageSwitcher = () => {
  const { language, setLanguage, t } = useLanguage();
  // OR for i18next:
  // const { i18n } = useTranslation();

  return (
    <select
      value={language}
      onChange={(e) => setLanguage(e.target.value as 'en' | 'id')}
      className="language-switcher"
    >
      <option value="en">English</option>
      <option value="id">Bahasa Indonesia</option>
    </select>
  );
};
```

### Guest Form Component

```typescript
import { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';

interface GuestFormProps {
  onSubmit: (data: any) => void;
}

export const GuestForm = ({ onSubmit }: GuestFormProps) => {
  const { t } = useLanguage();
  const [formData, setFormData] = useState({
    full_name: '',
    id_type: '',
    id_number: '',
    email: '',
    phone: '',
    phone_country_code: '',
    nationality: '',
    birth_date: '',
    is_vip: false,
    preferred_room_type_id: '',
    notes: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.full_name) {
      newErrors.full_name = t('messages.fieldRequired');
    } else if (formData.full_name.length < 2) {
      newErrors.full_name = t('validation.fullNameMin');
    } else if (formData.full_name.length > 100) {
      newErrors.full_name = t('validation.fullNameMax');
    }

    if (!formData.id_type) {
      newErrors.id_type = t('messages.fieldRequired');
    }

    if (!formData.id_number) {
      newErrors.id_number = t('validation.idNumberRequired');
    }

    if (formData.email && !isValidEmail(formData.email)) {
      newErrors.email = t('validation.invalidEmailFormat');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <fieldset>
        <legend>{t('form.requiredInformation')}</legend>

        <div className="form-group">
          <label htmlFor="fullName">{t('form.fullName')} *</label>
          <input
            id="fullName"
            type="text"
            placeholder={t('form.fullNamePlaceholder')}
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            aria-invalid={!!errors.full_name}
            aria-describedby={errors.full_name ? 'fullName-error' : undefined}
          />
          {errors.full_name && <span id="fullName-error" className="error">{errors.full_name}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="idType">{t('form.idType')} *</label>
          <select
            id="idType"
            value={formData.id_type}
            onChange={(e) => setFormData({ ...formData, id_type: e.target.value })}
            aria-invalid={!!errors.id_type}
            aria-describedby={errors.id_type ? 'idType-error' : undefined}
          >
            <option value="">{t('placeholders.selectOption')}</option>
            <option value="passport">{t('idTypes.passport')}</option>
            <option value="driver_license">{t('idTypes.driverLicense')}</option>
            <option value="national_id">{t('idTypes.nationalId')}</option>
            <option value="visa">{t('idTypes.visa')}</option>
            <option value="travel_document">{t('idTypes.travelDocument')}</option>
            <option value="other">{t('idTypes.other')}</option>
          </select>
          {errors.id_type && <span id="idType-error" className="error">{errors.id_type}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="idNumber">{t('form.idNumber')} *</label>
          <input
            id="idNumber"
            type="text"
            placeholder={t('form.idNumberPlaceholder')}
            value={formData.id_number}
            onChange={(e) => setFormData({ ...formData, id_number: e.target.value })}
            aria-invalid={!!errors.id_number}
            aria-describedby={errors.id_number ? 'idNumber-error' : undefined}
          />
          {errors.id_number && <span id="idNumber-error" className="error">{errors.id_number}</span>}
        </div>
      </fieldset>

      <fieldset>
        <legend>{t('form.additionalInformation')}</legend>

        <div className="form-group">
          <label htmlFor="email">{t('form.email')} ({t('form.optionalField')})</label>
          <input
            id="email"
            type="email"
            placeholder={t('form.emailPlaceholder')}
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label htmlFor="phone">{t('form.phone')} ({t('form.optionalField')})</label>
          <input
            id="phone"
            type="tel"
            placeholder={t('form.phonePlaceholder')}
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label htmlFor="nationality">{t('form.nationality')} ({t('form.optionalField')})</label>
          <input
            id="nationality"
            type="text"
            placeholder={t('form.nationalityPlaceholder')}
            value={formData.nationality}
            onChange={(e) => setFormData({ ...formData, nationality: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label htmlFor="birthDate">{t('form.dateOfBirth')} ({t('form.optionalField')})</label>
          <input
            id="birthDate"
            type="date"
            value={formData.birth_date}
            onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label htmlFor="vipStatus">{t('form.vipStatus')}</label>
          <input
            id="vipStatus"
            type="checkbox"
            checked={formData.is_vip}
            onChange={(e) => setFormData({ ...formData, is_vip: e.target.checked })}
          />
        </div>

        <div className="form-group">
          <label htmlFor="notes">{t('form.specialRequests')} ({t('form.optionalField')})</label>
          <textarea
            id="notes"
            placeholder={t('form.specialRequestsPlaceholder')}
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            rows={4}
          />
        </div>
      </fieldset>

      <button type="submit">{t('buttons.submit')}</button>
    </form>
  );
};

function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
```

---

## 📝 App.tsx Setup

```typescript
import { LanguageProvider } from './context/LanguageContext';
import { LanguageSwitcher } from './components/LanguageSwitcher';
import { GuestForm } from './components/GuestForm';

function App() {
  return (
    <LanguageProvider>
      <div className="app">
        <header>
          <h1>Hotel Management System</h1>
          <LanguageSwitcher />
        </header>

        <main>
          <GuestForm onSubmit={(data) => console.log(data)} />
        </main>
      </div>
    </LanguageProvider>
  );
}

export default App;
```

---

## ✅ Implementation Checklist

- [ ] Create `src/locales/en.json` with all English translations
- [ ] Create `src/locales/id.json` with all Indonesian translations
- [ ] Choose i18n implementation (i18next or custom context)
- [ ] Set up LanguageContext/i18n configuration
- [ ] Create LanguageSwitcher component
- [ ] Update GuestForm to use translations
- [ ] Update all other components to use translations
- [ ] Test language switching
- [ ] Verify translations display correctly
- [ ] Test on mobile devices
- [ ] Add language persistence (localStorage)
- [ ] Check for missing translations
- [ ] Test with long text (some languages are longer)
- [ ] Set up proper font support (especially for Indonesian)
- [ ] Document translation keys for team

---

## 🎯 Key Translation Keys for Guest Module

### Required
- `form.fullName`
- `form.idType`
- `form.idNumber`
- `buttons.submit`
- `messages.guestCreated`

### Optional but Important
- `form.email`
- `form.phone`
- `form.specialRequests`
- `buttons.uploadPhoto`
- `messages.photoUploadSuccess`
- `validation.emailAlreadyExists`

---

## 🔧 Vite + React + TypeScript Setup

**File: `vite.config.ts`** (no changes needed for i18n)

**File: `tsconfig.json`**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForEnumMembers": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "resolveJsonModule": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## 📚 Additional Resources

- **i18next Documentation:** https://www.i18next.com/
- **React i18next:** https://react.i18next.com/
- **Language Codes:** https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes
- **Currency Formatting:** Use `Intl.NumberFormat` for numbers/currency
- **Date Formatting:** Use `Intl.DateTimeFormat` for dates

---

## 🚀 Next Steps

1. Choose implementation method (i18next or custom context)
2. Create translation JSON files
3. Set up language context/i18n
4. Convert all UI text to use translations
5. Add language switcher
6. Test both languages
7. Deploy with bilingual support

---

**Version:** 1.0.0
**Last Updated:** November 8, 2025
**Supported Languages:** English (en), Indonesian (id)
**Implementation:** Ready for frontend development
