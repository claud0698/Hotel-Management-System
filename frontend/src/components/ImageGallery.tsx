/**
 * Image Gallery Component
 * Display images in thumbnail grid with lightbox/modal for full-size viewing
 */

import { useState } from 'react';
import type { RoomImage, RoomTypeImage } from '../services/api';

export type GalleryImage = RoomImage | RoomTypeImage;

export interface ImageGalleryProps {
  images: GalleryImage[];
  onDelete?: (imageId: number) => Promise<void>;
  isLoading?: boolean;
  emptyMessage?: string;
}

export function ImageGallery({
  images,
  onDelete,
  isLoading = false,
  emptyMessage = 'No images yet',
}: ImageGalleryProps) {
  const [selectedImageIndex, setSelectedImageIndex] = useState<number | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  if (images.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <p className="text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  const selectedImage = selectedImageIndex !== null ? images[selectedImageIndex] : null;

  const handleDelete = async (imageId: number) => {
    if (!onDelete) return;

    if (!confirm('Delete this image? This action cannot be undone.')) {
      return;
    }

    try {
      setDeleteError(null);
      await onDelete(imageId);
      setSelectedImageIndex(null);
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : 'Failed to delete image');
    }
  };

  const getImageTypeLabel = (imageType: string): string => {
    const typeMap: Record<string, string> = {
      // Room images
      main_photo: 'Main Photo',
      bedroom: 'Bedroom',
      bathroom: 'Bathroom',
      living_area: 'Living Area',
      amenities: 'Amenities',
      // Room Type images
      showcase: 'Showcase',
      floorplan: 'Floor Plan',
      // Generic
      other: 'Other',
    };
    return typeMap[imageType] || imageType;
  };

  const formatFileSize = (bytes: number | undefined): string => {
    if (!bytes) return 'N/A';
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  };

  return (
    <>
      {/* Thumbnail Grid */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Gallery ({images.length})</h3>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {images.map((image, index) => (
            <div
              key={image.id}
              className="relative group cursor-pointer rounded-lg overflow-hidden bg-gray-100 aspect-square hover:shadow-lg transition"
              onClick={() => setSelectedImageIndex(index)}
            >
              {/* Thumbnail Image */}
              <img
                src={image.image_path}
                alt={image.image_name}
                className="w-full h-full object-cover group-hover:opacity-75 transition"
                loading="lazy"
              />

              {/* Overlay on Hover */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
              </div>

              {/* Image Type Badge */}
              <div className="absolute top-2 left-2 bg-blue-600 text-white text-xs font-semibold px-2 py-1 rounded">
                {getImageTypeLabel(image.image_type)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Lightbox Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 z-50 bg-black bg-opacity-75 flex items-center justify-center p-4"
          onClick={() => setSelectedImageIndex(null)}
        >
          <div
            className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-screen flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {selectedImage.image_name}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  {getImageTypeLabel(selectedImage.image_type)}
                </p>
              </div>
              <button
                onClick={() => setSelectedImageIndex(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            {/* Image Content */}
            <div className="flex-1 overflow-auto flex items-center justify-center bg-gray-50 p-4">
              <img
                src={selectedImage.image_path}
                alt={selectedImage.image_name}
                className="max-w-full max-h-full object-contain"
              />
            </div>

            {/* Details */}
            <div className="bg-gray-50 p-4 border-t space-y-2 text-sm">
              {selectedImage.description && (
                <div>
                  <strong className="text-gray-700">Description:</strong>
                  <p className="text-gray-600 mt-1">{selectedImage.description}</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <strong className="text-gray-700">File Size:</strong>
                  <p className="text-gray-600">{formatFileSize(selectedImage.file_size_bytes)}</p>
                </div>
                <div>
                  <strong className="text-gray-700">Format:</strong>
                  <p className="text-gray-600">{selectedImage.mime_type || 'Unknown'}</p>
                </div>
                {selectedImage.image_width && selectedImage.image_height && (
                  <div>
                    <strong className="text-gray-700">Dimensions:</strong>
                    <p className="text-gray-600">
                      {selectedImage.image_width} × {selectedImage.image_height}px
                    </p>
                  </div>
                )}
                <div>
                  <strong className="text-gray-700">Uploaded:</strong>
                  <p className="text-gray-600">
                    {new Date(selectedImage.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Footer Actions */}
            <div className="flex items-center justify-between p-4 border-t gap-2">
              {/* Navigation */}
              <div className="flex gap-2">
                <button
                  onClick={() =>
                    setSelectedImageIndex((i) => (i === null ? null : i > 0 ? i - 1 : images.length - 1))
                  }
                  className="px-3 py-2 text-sm font-medium bg-gray-200 hover:bg-gray-300 rounded-lg transition"
                >
                  ← Previous
                </button>
                <span className="px-3 py-2 text-sm text-gray-600">
                  {selectedImageIndex !== null ? selectedImageIndex + 1 : 0} / {images.length}
                </span>
                <button
                  onClick={() =>
                    setSelectedImageIndex((i) => (i === null ? 0 : i < images.length - 1 ? i + 1 : 0))
                  }
                  className="px-3 py-2 text-sm font-medium bg-gray-200 hover:bg-gray-300 rounded-lg transition"
                >
                  Next →
                </button>
              </div>

              {/* Delete Button */}
              {onDelete && (
                <button
                  onClick={() => handleDelete(selectedImage.id)}
                  disabled={isLoading}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition"
                >
                  Delete
                </button>
              )}
            </div>

            {/* Error Message */}
            {deleteError && (
              <div className="p-4 bg-red-50 border-t border-red-200">
                <p className="text-red-700 text-sm">{deleteError}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
