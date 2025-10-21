import React, { useState, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQuery } from 'react-query';
import { Camera, Upload, FileText, Settings, X } from 'lucide-react';
import { notesService } from '../services/notesService.ts';
import { categoriesService } from '../services/categoriesService.ts';
import toast from 'react-hot-toast';

export const CapturePage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [ocrMode, setOcrMode] = useState('traditional');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: categories } = useQuery('categories', categoriesService.getCategories);

  const uploadMutation = useMutation(notesService.uploadNote, {
    onSuccess: (note) => {
      toast.success('Note uploaded successfully!');
      setSelectedFile(null);
      setPreview(null);
      setSelectedCategory(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Upload failed');
    },
  });

  const onDrop = (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
    },
    multiple: false
  });

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate({
        file: selectedFile,
        categoryId: selectedCategory || undefined,
        ocrMode
      });
    }
  };

  const handleCameraCapture = () => {
    // This would open camera - for now just show file input
    fileInputRef.current?.click();
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Capture Note</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload or capture a Rocketbook note to process with AI
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Area */}
        <div className="space-y-6">
          {/* Camera/Upload Options */}
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={handleCameraCapture}
              className="btn btn-secondary flex items-center justify-center py-4"
            >
              <Camera className="h-6 w-6 mr-2" />
              Take Photo
            </button>
            <div {...getRootProps()} className="btn btn-secondary flex items-center justify-center py-4 cursor-pointer">
              <Upload className="h-6 w-6 mr-2" />
              Upload File
            </div>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />

          {/* Drop Zone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-primary-400 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <Camera className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm text-gray-600">
              {isDragActive
                ? 'Drop the image here...'
                : 'Drag and drop an image, or click to select'}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Supports JPEG, PNG, GIF, BMP, WebP
            </p>
          </div>

          {/* Settings */}
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Processing Settings</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  OCR Mode
                </label>
                <select
                  value={ocrMode}
                  onChange={(e) => setOcrMode(e.target.value)}
                  className="input"
                >
                  <option value="traditional">Traditional (Fast, Offline)</option>
                  <option value="llm">LLM (Accurate, Online)</option>
                  <option value="auto">Auto (Best of Both)</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  {ocrMode === 'traditional' && 'Uses on-device processing for speed'}
                  {ocrMode === 'llm' && 'Uses AI for better accuracy with messy handwriting'}
                  {ocrMode === 'auto' && 'Automatically chooses the best method'}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category (Optional)
                </label>
                <select
                  value={selectedCategory || ''}
                  onChange={(e) => setSelectedCategory(e.target.value ? parseInt(e.target.value) : null)}
                  className="input"
                >
                  <option value="">No category</option>
                  {categories?.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Preview Area */}
        <div className="space-y-6">
          {preview ? (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Preview</h3>
                <button
                  onClick={() => {
                    setSelectedFile(null);
                    setPreview(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full h-64 object-contain border border-gray-200 rounded-lg"
                />
                
                <div className="text-sm text-gray-600">
                  <p><strong>File:</strong> {selectedFile?.name}</p>
                  <p><strong>Size:</strong> {selectedFile ? (selectedFile.size / 1024 / 1024).toFixed(2) : 0} MB</p>
                  <p><strong>Type:</strong> {selectedFile?.type}</p>
                </div>

                <button
                  onClick={handleUpload}
                  disabled={uploadMutation.isLoading}
                  className="w-full btn btn-primary disabled:opacity-50"
                >
                  {uploadMutation.isLoading ? 'Processing...' : 'Process Note'}
                </button>
              </div>
            </div>
          ) : (
            <div className="card">
              <div className="text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No image selected</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Upload or capture an image to see a preview
                </p>
              </div>
            </div>
          )}

          {/* Processing Status */}
          {uploadMutation.isLoading && (
            <div className="card">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mr-3"></div>
                <div>
                  <h3 className="text-sm font-medium text-gray-900">Processing Note</h3>
                  <p className="text-sm text-gray-500">
                    Running OCR and AI analysis...
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};