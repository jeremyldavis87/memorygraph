import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { Camera, FileText, Search, Plus, TrendingUp, Clock } from 'lucide-react';
import { notesService } from '../services/notesService.ts';

export const DashboardPage: React.FC = () => {
  const { data: recentNotes, isLoading: notesLoading } = useQuery(
    'recent-notes',
    () => notesService.getNotes({ limit: 5 }),
    { refetchOnWindowFocus: false }
  );

  const stats = [
    { name: 'Total Notes', value: recentNotes?.total || 0, icon: FileText },
    { name: 'This Week', value: '12', icon: TrendingUp },
    { name: 'Processing', value: '3', icon: Clock },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back! Here's what's happening with your knowledge base.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Link
          to="/capture"
          className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:shadow-md transition-shadow"
        >
          <div>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Camera className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-900">Capture Note</h3>
                <p className="text-sm text-gray-500">Scan a Rocketbook note</p>
              </div>
            </div>
          </div>
        </Link>

        <Link
          to="/notes"
          className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:shadow-md transition-shadow"
        >
          <div>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileText className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-900">View Notes</h3>
                <p className="text-sm text-gray-500">Browse your knowledge base</p>
              </div>
            </div>
          </div>
        </Link>

        <Link
          to="/search"
          className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:shadow-md transition-shadow"
        >
          <div>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Search className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-900">Search</h3>
                <p className="text-sm text-gray-500">Find information quickly</p>
              </div>
            </div>
          </div>
        </Link>

        <button className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:shadow-md transition-shadow">
          <div>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Plus className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-900">Quick Add</h3>
                <p className="text-sm text-gray-500">Add a quick note</p>
              </div>
            </div>
          </div>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Icon className="h-8 w-8 text-primary-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.name}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stat.value}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Notes */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Recent Notes</h3>
        </div>
        <div className="space-y-4">
          {notesLoading ? (
            <div className="animate-pulse space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          ) : recentNotes?.notes?.length ? (
            recentNotes.notes.map((note) => (
              <div key={note.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 truncate">
                    {note.title}
                  </h4>
                  <p className="text-sm text-gray-500 truncate">
                    {note.summary || note.content || 'No content'}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(note.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="ml-4 flex-shrink-0">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                    {note.source_type}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No notes yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by capturing your first note.
              </p>
              <div className="mt-6">
                <Link
                  to="/capture"
                  className="btn btn-primary"
                >
                  <Camera className="h-4 w-4 mr-2" />
                  Capture Note
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};