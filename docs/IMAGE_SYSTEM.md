# Hotel Management System - Image Management System

## Overview

The image management system provides comprehensive support for uploading, storing, and displaying images for rooms and room types. It supports multiple storage locations and image types.

---

## Architecture

### Database Schema

#### RoomImage Table
Stores images for individual rooms.

```sql
CREATE TABLE room_images (
  id SERIAL PRIMARY KEY,
  room_id INTEGER NOT NULL REFERENCES rooms(id),
  image_name VARCHAR(255) NOT NULL,
  image_type VARCHAR(20) NOT NULL,  -- main_photo, bedroom, bathroom, living_area, amenities, other
  image_path VARCHAR(500) NOT NULL,
  storage_location VARCHAR(50) NOT NULL,  -- local, s3, gcs, azure
  file_size_bytes INTEGER,
  mime_type VARCHAR(100),
  original_filename VARCHAR(255),
  image_width INTEGER,
  image_height INTEGER,
  uploaded_by INTEGER REFERENCES users(id),
  description TEXT,
  display_order INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Image Types for Rooms:**
- `main_photo` - Primary/cover photo of the room
- `bedroom` - Bedroom area photo
- `bathroom` - Bathroom/washroom photo
- `living_area` - Living/sitting area photo
- `amenities` - Room amenities/features photo
- `other` - Miscellaneous photos

#### RoomTypeImage Table
Stores showcase images for room types (e.g., "Standard Room type gallery").

```sql
CREATE TABLE room_type_images (
  id SERIAL PRIMARY KEY,
  room_type_id INTEGER NOT NULL REFERENCES room_types(id),
  image_name VARCHAR(255) NOT NULL,
  image_type VARCHAR(20) NOT NULL,  -- showcase, floorplan, amenities, other
  image_path VARCHAR(500) NOT NULL,
  storage_location VARCHAR(50) NOT NULL,  -- local, s3, gcs, azure
  file_size_bytes INTEGER,
  mime_type VARCHAR(100),
  original_filename VARCHAR(255),
  image_width INTEGER,
  image_height INTEGER,
  uploaded_by INTEGER REFERENCES users(id),
  description TEXT,
  display_order INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Image Types for Room Types:**
- `showcase` - Gallery/promotional images of the room type
- `floorplan` - Floor plan or layout diagram
- `amenities` - Room type amenities/features
- `other` - Additional images

---

## Storage Locations

The system supports multiple cloud storage backends:

| Location | Provider | Setup Required |
|----------|----------|-----------------|
| `local` | File system (local storage) | Configure local upload directory |
| `s3` | AWS S3 | AWS credentials & bucket setup |
| `gcs` | Google Cloud Storage | GCP credentials & bucket setup |
| `azure` | Azure Blob Storage | Azure connection string & container |

### Recommended Storage Sizes
- **Local**: For development/testing only (max ~100MB)
- **S3/GCS/Azure**: For production (virtually unlimited)

---

## API Endpoints

### Room Images

#### Get Room Images
```
GET /api/rooms/{roomId}/images
Response: { images: RoomImage[] }
```

#### Get Single Room Image
```
GET /api/rooms/{roomId}/images/{imageId}
Response: { image: RoomImage }
```

#### Upload Room Image
```
POST /api/rooms/{roomId}/images
Content-Type: multipart/form-data

Form Data:
- file: File
- image_type: 'main_photo' | 'bedroom' | 'bathroom' | 'living_area' | 'amenities' | 'other'
- description?: string

Response: { image: RoomImage }
```

#### Delete Room Image
```
DELETE /api/rooms/{roomId}/images/{imageId}
Response: { message: string }
```

#### Reorder Room Images
```
POST /api/rooms/{roomId}/images/reorder
Body: {
  images: [
    { id: number, display_order: number },
    ...
  ]
}
Response: { message: string }
```

### Room Type Images

#### Get Room Type Images
```
GET /api/rooms/types/{roomTypeId}/images
Response: { images: RoomTypeImage[] }
```

#### Upload Room Type Image
```
POST /api/rooms/types/{roomTypeId}/images
Content-Type: multipart/form-data

Form Data:
- file: File
- image_type: 'showcase' | 'floorplan' | 'amenities' | 'other'
- description?: string

Response: { image: RoomTypeImage }
```

#### Delete Room Type Image
```
DELETE /api/rooms/types/{roomTypeId}/images/{imageId}
Response: { message: string }
```

---

## Frontend Components

### ImageUploader Component
Reusable component for uploading images with file validation and error handling.

**Usage:**
```tsx
import { ImageUploader } from '../components/ImageUploader';
import { apiClient } from '../services/api';

<ImageUploader
  onUpload={async (file, imageType, description) => {
    await apiClient.uploadRoomImage(roomId, file, imageType, description);
  }}
  imageTypes={[
    { value: 'main_photo', label: 'Main Photo' },
    { value: 'bedroom', label: 'Bedroom' },
    { value: 'bathroom', label: 'Bathroom' },
    { value: 'living_area', label: 'Living Area' },
    { value: 'amenities', label: 'Amenities' },
    { value: 'other', label: 'Other' },
  ]}
  maxFileSize={5}
  acceptedFormats={['image/jpeg', 'image/png', 'image/webp']}
/>
```

**Features:**
- Drag-and-drop file selection
- File size validation
- File type validation
- Image type selection dropdown
- Optional description
- Loading state management
- Error/success messages

### ImageGallery Component
Display images in a responsive thumbnail grid with lightbox modal for full-size viewing.

**Usage:**
```tsx
import { ImageGallery } from '../components/ImageGallery';

<ImageGallery
  images={roomImages}
  onDelete={async (imageId) => {
    await apiClient.deleteRoomImage(roomId, imageId);
  }}
  isLoading={isDeleting}
  emptyMessage="No images uploaded yet"
/>
```

**Features:**
- Responsive thumbnail grid
- Lightbox modal for full-size viewing
- Image navigation (previous/next)
- Image metadata display
- Delete functionality
- File size formatting
- Image dimensions display

---

## TypeScript Interfaces

### RoomImage
```typescript
interface RoomImage {
  id: number;
  room_id: number;
  image_name: string;
  image_type: 'main_photo' | 'bedroom' | 'bathroom' | 'living_area' | 'amenities' | 'other';
  image_path: string;
  storage_location: 'local' | 's3' | 'gcs' | 'azure';
  file_size_bytes?: number;
  mime_type?: string;
  original_filename?: string;
  image_width?: number;
  image_height?: number;
  uploaded_by?: number;
  description?: string;
  display_order?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

### RoomTypeImage
```typescript
interface RoomTypeImage {
  id: number;
  room_type_id: number;
  image_name: string;
  image_type: 'showcase' | 'floorplan' | 'amenities' | 'other';
  image_path: string;
  storage_location: 'local' | 's3' | 'gcs' | 'azure';
  file_size_bytes?: number;
  mime_type?: string;
  original_filename?: string;
  image_width?: number;
  image_height?: number;
  uploaded_by?: number;
  description?: string;
  display_order?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

---

## API Client Methods

### ApiClient Image Methods
```typescript
// Room Images
async getRoomImages(roomId: number): Promise<{ images: RoomImage[] }>
async getRoomImage(roomId: number, imageId: number): Promise<{ image: RoomImage }>
async uploadRoomImage(roomId: number, file: File, imageType: string, description?: string): Promise<{ image: RoomImage }>
async deleteRoomImage(roomId: number, imageId: number): Promise<{ message: string }>
async updateRoomImageOrder(roomId: number, imageUpdates: Array<{ id: number; display_order: number }>): Promise<{ message: string }>

// Room Type Images
async getRoomTypeImages(roomTypeId: number): Promise<{ images: RoomTypeImage[] }>
async uploadRoomTypeImage(roomTypeId: number, file: File, imageType: string, description?: string): Promise<{ image: RoomTypeImage }>
async deleteRoomTypeImage(roomTypeId: number, imageId: number): Promise<{ message: string }>
```

---

## Constraints & Validation

### File Constraints
- **Max File Size**: 5MB (configurable)
- **Accepted Formats**: JPEG, PNG, WebP
- **Dimensions**: Recommended min 800x600px, max 4000x3000px

### Display Constraints
- **Thumbnail Size**: 200x200px (CSS aspect-square)
- **Lightbox Size**: Max 1024x768px (responsive)
- **Display Order**: 0-based integer (for sorting in galleries)

### Active Status
- Images with `is_active = false` are soft-deleted (not shown in galleries)
- Permanent deletion removes from storage and database

---

## Implementation Status

### ✅ Completed
- [x] Database models (RoomImage, RoomTypeImage)
- [x] API interfaces (TypeScript)
- [x] API client methods (frontend)
- [x] ImageUploader component
- [x] ImageGallery component with lightbox
- [x] Image type constants and validation

### 🔄 In Progress
- [ ] Backend API endpoints implementation
- [ ] Image storage handler (local/S3/GCS/Azure)
- [ ] Image optimization and resizing
- [ ] Image CDN integration

### 📋 Not Yet Implemented
- [ ] Drag-and-drop reordering in gallery
- [ ] Batch upload support
- [ ] Image cropping/editing interface
- [ ] Watermarking support
- [ ] Image compression/optimization
- [ ] Automatic thumbnail generation
- [ ] WebP conversion for optimization

---

## File Structure

**Frontend Components:**
```
frontend/src/components/
├── ImageUploader.tsx      # File upload component
└── ImageGallery.tsx       # Gallery display component

frontend/src/services/
└── api.ts                 # API client with image methods
```

**Backend Models:**
```
backend/
├── models.py              # RoomImage, RoomTypeImage models
└── routes/               # (to be created)
    └── image_router.py    # Image endpoints (future)
```

---

## Example Usage

### Integrating into RoomDetailPage

```tsx
import { ImageUploader } from '../components/ImageUploader';
import { ImageGallery } from '../components/ImageGallery';

export function RoomDetailPage() {
  const [roomImages, setRoomImages] = useState<RoomImage[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleUploadImage = async (file: File, imageType: string, description?: string) => {
    setIsUploading(true);
    try {
      const result = await apiClient.uploadRoomImage(roomId, file, imageType, description);
      setRoomImages([...roomImages, result.image]);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteImage = async (imageId: number) => {
    await apiClient.deleteRoomImage(roomId, imageId);
    setRoomImages(roomImages.filter(img => img.id !== imageId));
  };

  return (
    <div className="space-y-6">
      <ImageUploader
        onUpload={handleUploadImage}
        imageTypes={ROOM_IMAGE_TYPES}
        isLoading={isUploading}
      />

      <ImageGallery
        images={roomImages}
        onDelete={handleDeleteImage}
      />
    </div>
  );
}
```

---

## Best Practices

1. **File Size Management**: Always validate file size on client before upload
2. **Error Handling**: Provide clear error messages for upload failures
3. **Caching**: Cache images appropriately based on storage location
4. **Cleanup**: Delete images from storage when removing from database
5. **Optimization**: Consider lazy-loading for galleries with many images
6. **Accessibility**: Include alt text and proper semantic HTML for images
7. **Security**: Validate file types on backend (don't trust client validation)

---

## References
- [Room Management Documentation](./ROOM_MANAGEMENT.md)
- [API Documentation](./API.md)
- [Database Schema](../backend/models.py)
