/**
 * Image Uploader Component
 * Reusable component for uploading images (room images, room type images, etc.)
 */

import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export interface ImageUploaderProps {
  onUpload: (file: File, imageType: string, description?: string) => Promise<void>;
  imageTypes: Array<{ value: string; label: string }>;
  isLoading?: boolean;
  maxFileSize?: number; // in MB
  acceptedFormats?: string[];
}

export function ImageUploader({
  onUpload,
  imageTypes,
  isLoading = false,
  maxFileSize = 5,
  acceptedFormats = ['image/jpeg', 'image/png', 'image/webp'],
}: ImageUploaderProps) {
  const { t } = useTranslation();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedImageType, setSelectedImageType] = useState<string>(imageTypes[0]?.value || '');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    setError(null);
    setSuccess(null);

    if (!file) return;

    // Validate file size
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxFileSize) {
      setError(`File size exceeds ${maxFileSize}MB limit`);
      return;
    }

    // Validate file type
    if (!acceptedFormats.includes(file.type)) {
      setError(`File type not supported. Accepted: ${acceptedFormats.join(', ')}`);
      return;
    }

    setSelectedFile(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    if (!selectedImageType) {
      setError('Please select image type');
      return;
    }

    try {
      await onUpload(selectedFile, selectedImageType, description || undefined);
      setSuccess('Image uploaded successfully');
      setSelectedFile(null);
      setDescription('');
      setSelectedImageType(imageTypes[0]?.value || '');

      // Reset file input
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload image');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Image</h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* File Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Image File *
          </label>
          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <svg
                  className="w-8 h-8 text-gray-400 mb-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                <p className="text-sm text-gray-600">
                  {selectedFile ? selectedFile.name : 'Click to select image'}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Max {maxFileSize}MB • PNG, JPG, WebP
                </p>
              </div>
              <input
                type="file"
                accept={acceptedFormats.join(',')}
                onChange={handleFileSelect}
                disabled={isLoading}
                className="hidden"
              />
            </label>
          </div>
        </div>

        {/* Image Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Image Type *
          </label>
          <select
            value={selectedImageType}
            onChange={(e) => setSelectedImageType(e.target.value)}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Select Type --</option>
            {imageTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description (Optional)
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isLoading}
            placeholder="Add a description for this image..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-md">
            <p className="text-green-700 text-sm">{success}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !selectedFile}
          className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition"
        >
          {isLoading ? 'Uploading...' : 'Upload Image'}
        </button>
      </form>
    </div>
  );
}
