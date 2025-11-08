# Guest Check-In Checklist

## English | Bahasa Indonesia

---

## 📋 Guest Information Checklist

### ✅ REQUIRED INFORMATION (Must Collect)

| English | Bahasa Indonesia | Field Name | Type | Max Length |
|---------|-----------------|-----------|------|-----------|
| **Full Name** | **Nama Lengkap** | full_name | Text | 100 chars |
| **ID Type** | **Tipe ID** | id_type | Select | 50 chars |
| **ID Number** | **Nomor ID** | id_number | Text | 50 chars |

### Examples for ID Type (Tipe ID):
- Passport / Paspor
- Driver License / SIM (Surat Izin Mengemudi)
- National ID / KTP (Kartu Tanda Penduduk)
- Visa / Visa
- Travel Document / Dokumen Perjalanan

---

### ℹ️ OPTIONAL INFORMATION (Additional Details)

| English | Bahasa Indonesia | Field Name | Type | Notes |
|---------|-----------------|-----------|------|-------|
| Email Address | Alamat Email | email | Email | Must be unique |
| Phone Number | Nomor Telepon | phone | Text | Max 20 chars |
| Country Code | Kode Negara | phone_country_code | Text | e.g., +1, +62, +886 |
| Nationality | Kewarganegaraan | nationality | Text | Country name |
| Date of Birth | Tanggal Lahir | birth_date | Date | Format: YYYY-MM-DD |
| VIP Status | Status VIP | is_vip | Toggle | Yes/No |
| Preferred Room Type | Tipe Kamar Pilihan | preferred_room_type_id | Select | Single/Double/Suite |
| Special Requests | Permintaan Khusus | notes | Text Area | Unlimited |

---

## 📸 ID Photo Upload Checklist

### English Instructions

1. **Prepare the ID Document**
   - Ensure the ID is clean and clearly visible
   - Check that all important information (name, number, issue/expiry date) is readable
   - Remove any protective covers or cases

2. **Photograph/Scan the ID**
   - Use phone camera or scanner
   - Ensure good lighting and no shadows
   - Capture the front side clearly
   - For double-sided IDs, photograph both sides

3. **Select Photo Type**
   - id_photo (for general ID documents)
   - passport_photo (for passports)
   - license_photo (for driver's licenses)
   - visa_photo (for visa pages)

4. **Upload the File**
   - Click "Upload ID Photo" button
   - Select the image file (JPEG or PNG)
   - Wait for upload confirmation
   - File will be stored with guest record

5. **Verify Upload Success**
   - Confirm file appears in guest's photo gallery
   - Check image quality and readability
   - File is saved and can be retrieved later

---

### Panduan Bahasa Indonesia

1. **Siapkan Dokumen ID**
   - Pastikan ID bersih dan terlihat jelas
   - Periksa semua informasi penting (nama, nomor, tanggal terbit/kadaluarsa) dapat dibaca
   - Lepas penutup atau casing pelindung

2. **Ambil Foto/Pindai ID**
   - Gunakan kamera ponsel atau scanner
   - Pastikan pencahayaan baik tanpa bayangan
   - Tangkap sisi depan dengan jelas
   - Untuk ID dua sisi, foto kedua sisinya

3. **Pilih Tipe Foto**
   - id_photo (untuk dokumen ID umum)
   - passport_photo (untuk paspor)
   - license_photo (untuk SIM)
   - visa_photo (untuk halaman visa)

4. **Unggah File**
   - Klik tombol "Upload Foto ID"
   - Pilih file gambar (JPEG atau PNG)
   - Tunggu konfirmasi unggahan
   - File akan disimpan dengan catatan tamu

5. **Verifikasi Unggahan Berhasil**
   - Konfirmasi file muncul di galeri foto tamu
   - Periksa kualitas gambar dan keterbacaan
   - File tersimpan dan dapat diambil nanti

---

## 🔐 Data Storage Locations

### ID Information (Required Fields)
```
Database Table: guests
Fields:
  - full_name (indexed)
  - id_type
  - id_number
```

### Optional Guest Info
```
Database Table: guests
Fields:
  - email (indexed, unique)
  - phone (indexed)
  - phone_country_code
  - nationality
  - birth_date
  - is_vip (boolean)
  - preferred_room_type_id (foreign key)
  - notes (unlimited text)
```

### ID Photos Storage
```
Database Table: guest_images
File Storage: uploads/guests/{guest_id}/
Files Stored As: {image_type}_{guest_id}_{random}.{ext}

Metadata Tracked:
  - image_id (primary key)
  - guest_id (foreign key)
  - image_type (id_photo, passport_photo, license_photo, visa_photo)
  - file_path (storage location)
  - file_name (uploaded file name)
  - file_size (bytes)
  - mime_type (image/jpeg, image/png, application/pdf)
  - uploaded_by_user_id (receptionist ID)
  - created_at (upload timestamp)
```

---

## 🌐 Frontend Bilingual Implementation

### Labels & Translations

```typescript
// English Labels
const EN = {
  form: {
    fullName: "Full Name",
    idType: "ID Type",
    idNumber: "ID Number",
    email: "Email Address",
    phone: "Phone Number",
    countryCode: "Country Code",
    nationality: "Nationality",
    dateOfBirth: "Date of Birth",
    vipStatus: "VIP Status",
    preferredRoomType: "Preferred Room Type",
    specialRequests: "Special Requests / Notes",
  },
  buttons: {
    submit: "Create Guest",
    uploadPhoto: "Upload ID Photo",
    viewPhotos: "View Photos",
    deletePhoto: "Delete Photo",
    update: "Update Guest",
    cancel: "Cancel",
  },
  messages: {
    required: "This field is required",
    invalidEmail: "Please enter a valid email",
    photoUploadSuccess: "Photo uploaded successfully",
    photoUploadError: "Failed to upload photo",
    guestCreated: "Guest created successfully",
    guestUpdated: "Guest updated successfully",
  },
  validation: {
    fullNameMin: "Full name must be at least 2 characters",
    fullNameMax: "Full name cannot exceed 100 characters",
    idNumberRequired: "ID number is required",
    invalidPhoneFormat: "Please enter a valid phone number",
  }
};

// Indonesian Labels
const ID = {
  form: {
    fullName: "Nama Lengkap",
    idType: "Tipe ID",
    idNumber: "Nomor ID",
    email: "Alamat Email",
    phone: "Nomor Telepon",
    countryCode: "Kode Negara",
    nationality: "Kewarganegaraan",
    dateOfBirth: "Tanggal Lahir",
    vipStatus: "Status VIP",
    preferredRoomType: "Tipe Kamar Pilihan",
    specialRequests: "Permintaan Khusus / Catatan",
  },
  buttons: {
    submit: "Buat Tamu",
    uploadPhoto: "Unggah Foto ID",
    viewPhotos: "Lihat Foto",
    deletePhoto: "Hapus Foto",
    update: "Perbarui Tamu",
    cancel: "Batal",
  },
  messages: {
    required: "Bidang ini wajib diisi",
    invalidEmail: "Masukkan email yang valid",
    photoUploadSuccess: "Foto berhasil diunggah",
    photoUploadError: "Gagal mengunggah foto",
    guestCreated: "Tamu berhasil dibuat",
    guestUpdated: "Tamu berhasil diperbarui",
  },
  validation: {
    fullNameMin: "Nama lengkap minimal 2 karakter",
    fullNameMax: "Nama lengkap tidak boleh lebih dari 100 karakter",
    idNumberRequired: "Nomor ID wajib diisi",
    invalidPhoneFormat: "Masukkan format nomor telepon yang valid",
  }
};
```

### ID Type Options (Bilingual)

```typescript
const ID_TYPES = [
  { value: "passport", en: "Passport", id: "Paspor" },
  { value: "driver_license", en: "Driver License", id: "SIM" },
  { value: "national_id", en: "National ID", id: "KTP" },
  { value: "visa", en: "Visa", id: "Visa" },
  { value: "travel_document", en: "Travel Document", id: "Dokumen Perjalanan" },
  { value: "other", en: "Other", id: "Lainnya" },
];
```

### Room Type Options (Bilingual)

```typescript
const ROOM_TYPES = [
  { value: 1, en: "Single Room", id: "Kamar Single" },
  { value: 2, en: "Double Room", id: "Kamar Double" },
  { value: 3, en: "Suite", id: "Suite" },
  { value: 4, en: "Deluxe Suite", id: "Suite Mewah" },
];
```

### Photo Type Options (Bilingual)

```typescript
const PHOTO_TYPES = [
  { value: "id_photo", en: "ID Photo", id: "Foto ID" },
  { value: "passport_photo", en: "Passport Photo", id: "Foto Paspor" },
  { value: "license_photo", en: "License Photo", id: "Foto SIM" },
  { value: "visa_photo", en: "Visa Photo", id: "Foto Visa" },
];
```

---

## 📱 Form Fields Implementation

### Create Guest Form (Bilingual)

```typescript
// Required Fields Section
<FormSection title={lang === 'en' ? 'Required Information' : 'Informasi Wajib'}>
  <TextField
    label={labels.form.fullName}
    required
    minLength={2}
    maxLength={100}
  />

  <SelectField
    label={labels.form.idType}
    required
    options={ID_TYPES.map(t => ({ label: lang === 'en' ? t.en : t.id, value: t.value }))}
  />

  <TextField
    label={labels.form.idNumber}
    required
    maxLength={50}
  />
</FormSection>

// Optional Fields Section
<FormSection title={lang === 'en' ? 'Additional Information' : 'Informasi Tambahan'}>
  <EmailField
    label={labels.form.email}
    optional
  />

  <PhoneField
    label={labels.form.phone}
    optional
    maxLength={20}
  />

  <SelectField
    label={labels.form.countryCode}
    optional
    options={COUNTRY_CODES}
  />

  <TextField
    label={labels.form.nationality}
    optional
    maxLength={50}
  />

  <DateField
    label={labels.form.dateOfBirth}
    optional
    format="YYYY-MM-DD"
  />

  <ToggleField
    label={labels.form.vipStatus}
    optional
  />

  <SelectField
    label={labels.form.preferredRoomType}
    optional
    options={ROOM_TYPES.map(r => ({ label: lang === 'en' ? r.en : r.id, value: r.value }))}
  />

  <TextAreaField
    label={labels.form.specialRequests}
    optional
    placeholder={lang === 'en' ? 'E.g., high floor, non-smoking, allergies...' : 'Cth: lantai tinggi, bebas asap, alergi...'}
  />
</FormSection>
```

### Photo Upload Section (Bilingual)

```typescript
<PhotoUploadSection>
  <SelectField
    label={labels.form.idType}
    options={PHOTO_TYPES.map(p => ({ label: lang === 'en' ? p.en : p.id, value: p.value }))}
  />

  <FileUpload
    accept=".jpg,.jpeg,.png,.pdf"
    maxSize={5000000} // 5MB
    onUpload={handlePhotoUpload}
  />

  <Button>{labels.buttons.uploadPhoto}</Button>
</PhotoUploadSection>

// Display Photos
<PhotoGallery>
  {photos.map(photo => (
    <PhotoCard
      key={photo.id}
      photo={photo}
      type={lang === 'en' ? PHOTO_TYPES.find(p => p.value === photo.image_type)?.en :
                           PHOTO_TYPES.find(p => p.value === photo.image_type)?.id}
      onDelete={() => handleDeletePhoto(photo.id)}
    />
  ))}
</PhotoGallery>
```

---

## ✅ Frontend Checklist for Developers

- [ ] Create `locales/en.json` with all English labels
- [ ] Create `locales/id.json` with all Indonesian labels
- [ ] Implement language switcher (toggle button)
- [ ] Create GuestForm component with bilingual labels
- [ ] Add form validation with bilingual error messages
- [ ] Implement photo upload with file type validation
- [ ] Create photo gallery display component
- [ ] Add loading states for file uploads
- [ ] Test with both English and Indonesian
- [ ] Verify all form fields are labeled in both languages
- [ ] Test ID photo upload and retrieval
- [ ] Verify form submission sends data to API correctly
- [ ] Add success/error messages in both languages
- [ ] Test on mobile devices for responsiveness

---

## 🔗 API Integration Notes

### Create Guest Endpoint
```
POST /api/guests

Required:
- full_name (string, 2-100 chars)
- id_type (string, max 50 chars)
- id_number (string, max 50 chars)

Optional:
- email (string, unique)
- phone (string, max 20)
- phone_country_code (string, max 5)
- nationality (string, max 50)
- birth_date (string, YYYY-MM-DD)
- is_vip (boolean)
- preferred_room_type_id (integer)
- notes (string, unlimited)
```

### Upload ID Photo Endpoint
```
POST /api/guests/{guest_id}/upload-id-photo

Query Parameters:
- image_type (string): id_photo, passport_photo, license_photo, visa_photo

Form Data:
- file (file): JPEG, PNG, or PDF

Response:
- id (photo record ID)
- guest_id
- image_type
- file_path
- file_name
- file_size
- mime_type
- uploaded_by_user_id
- created_at
```

### Get Guest Photos Endpoint
```
GET /api/guests/{guest_id}/photos

Returns: Array of photo objects with metadata
```

### Delete Photo Endpoint
```
DELETE /api/guests/{guest_id}/photos/{photo_id}

Returns: Success message
```

---

## 📝 Notes

- All form fields should have clear labels in both English and Indonesian
- Error messages must be bilingual
- Validation messages should match language selection
- Country code should be optional but suggested for international guests
- ID photo upload is separate from guest creation (can be done after)
- Multiple photos can be uploaded per guest (passport, ID, visa, etc.)
- Photos are stored locally in `uploads/guests/{guest_id}/` directory
- File type validation: JPEG, PNG, PDF only
- Max file size: 5MB (can be adjusted in frontend)

---

**Version:** 1.0.0
**Last Updated:** November 8, 2025
**Language Support:** English (EN) & Indonesian (ID)
