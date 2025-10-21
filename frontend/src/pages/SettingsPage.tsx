import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../contexts/AuthContext';
import { useMutation, useQuery } from 'react-query';
import { Save, User, Camera, Brain, Shield } from 'lucide-react';
import toast from 'react-hot-toast';

interface SettingsForm {
  full_name?: string;
  default_ocr_mode: string;
  auto_capture: boolean;
  ai_processing_enabled: boolean;
}

export const SettingsPage: React.FC = () => {
  const { user, login } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<SettingsForm>({
    defaultValues: {
      full_name: user?.full_name || '',
      default_ocr_mode: user?.default_ocr_mode || 'traditional',
      auto_capture: user?.auto_capture || true,
      ai_processing_enabled: user?.ai_processing_enabled || true,
    }
  });

  const updateSettingsMutation = useMutation(
    async (data: SettingsForm) => {
      // This would call an API endpoint to update user settings
      // For now, we'll just simulate it
      return new Promise(resolve => setTimeout(resolve, 1000));
    },
    {
      onSuccess: () => {
        toast.success('Settings updated successfully!');
      },
      onError: () => {
        toast.error('Failed to update settings');
      }
    }
  );

  const onSubmit = (data: SettingsForm) => {
    updateSettingsMutation.mutate(data);
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'capture', name: 'Capture', icon: Camera },
    { id: 'ai', name: 'AI Settings', icon: Brain },
    { id: 'privacy', name: 'Privacy', icon: Shield },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <nav className="space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    activeTab === tab.id
                      ? 'bg-primary-100 text-primary-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {activeTab === 'profile' && (
              <div className="card">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Full Name
                    </label>
                    <input
                      {...register('full_name')}
                      type="text"
                      className="input"
                      placeholder="Enter your full name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={user?.email || ''}
                      disabled
                      className="input bg-gray-50"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Email cannot be changed
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Username
                    </label>
                    <input
                      type="text"
                      value={user?.username || ''}
                      disabled
                      className="input bg-gray-50"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Username cannot be changed
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'capture' && (
              <div className="card">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Capture Settings</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Default OCR Mode
                    </label>
                    <select
                      {...register('default_ocr_mode')}
                      className="input"
                    >
                      <option value="traditional">Traditional (Fast, Offline)</option>
                      <option value="llm">LLM (Accurate, Online)</option>
                      <option value="auto">Auto (Best of Both)</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-1">
                      Choose the default OCR processing mode for new captures
                    </p>
                  </div>
                  <div className="flex items-center">
                    <input
                      {...register('auto_capture')}
                      type="checkbox"
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-700">
                      Enable auto-capture
                    </label>
                  </div>
                  <p className="text-xs text-gray-500">
                    Automatically capture notes when QR code is detected
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'ai' && (
              <div className="card">
                <h3 className="text-lg font-medium text-gray-900 mb-4">AI Settings</h3>
                <div className="space-y-4">
                  <div className="flex items-center">
                    <input
                      {...register('ai_processing_enabled')}
                      type="checkbox"
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-700">
                      Enable AI processing
                    </label>
                  </div>
                  <p className="text-xs text-gray-500">
                    Allow AI to analyze your notes for entities, summaries, and insights
                  </p>
                  
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-blue-900 mb-2">AI Features</h4>
                    <ul className="text-xs text-blue-800 space-y-1">
                      <li>• Automatic entity extraction (people, projects, concepts)</li>
                      <li>• Smart summaries and insights</li>
                      <li>• Action item detection</li>
                      <li>• Related note suggestions</li>
                      <li>• Knowledge graph construction</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'privacy' && (
              <div className="card">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Privacy & Security</h3>
                <div className="space-y-4">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-green-900 mb-2">Data Ownership</h4>
                    <p className="text-xs text-green-800">
                      You own all your data. Export or delete your information at any time.
                    </p>
                  </div>
                  
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-yellow-900 mb-2">AI Processing</h4>
                    <p className="text-xs text-yellow-800">
                      AI processing is optional and can be disabled. When enabled, your data is processed securely and not used for training.
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <button type="button" className="btn btn-secondary text-sm">
                      Export My Data
                    </button>
                    <button type="button" className="btn btn-danger text-sm">
                      Delete Account
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={isSubmitting || updateSettingsMutation.isLoading}
                className="btn btn-primary disabled:opacity-50"
              >
                <Save className="h-4 w-4 mr-2" />
                {isSubmitting || updateSettingsMutation.isLoading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};