import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { Search, Filter, FileText, Calendar, Tag, Eye } from 'lucide-react';
import { notesService } from '../services/notesService';
import { categoriesService } from '../services/categoriesService';

export const NotesPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  const { data: notes, isLoading } = useQuery(
    ['notes', searchQuery, selectedCategory, currentPage],
    () => notesService.getNotes({
      search: searchQuery || undefined,
      category_id: selectedCategory || undefined,
      skip: (currentPage - 1) * pageSize,
      limit: pageSize
    })
  );

  const { data: categories } = useQuery('categories', categoriesService.getCategories);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Notes</h1>
        <p className="mt-1 text-sm text-gray-500">
          Browse and search through your knowledge base
        </p>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search notes..."
                  className="input pl-10"
                />
              </div>
            </div>
            <div className="sm:w-48">
              <select
                value={selectedCategory || ''}
                onChange={(e) => setSelectedCategory(e.target.value ? parseInt(e.target.value) : null)}
                className="input"
              >
                <option value="">All Categories</option>
                {categories?.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
            <button type="submit" className="btn btn-primary">
              Search
            </button>
          </div>
        </form>
      </div>

      {/* Notes List */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : notes?.notes?.length ? (
          notes.notes.map((note) => (
            <div key={note.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className="text-lg font-medium text-gray-900 truncate">
                      {note.title}
                    </h3>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                      {note.source_type}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {note.summary || note.content || note.original_text || 'No content available'}
                  </p>
                  
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <div className="flex items-center">
                      <Calendar className="h-3 w-3 mr-1" />
                      {new Date(note.created_at).toLocaleDateString()}
                    </div>
                    {note.ocr_confidence && (
                      <div className="flex items-center">
                        <span className="mr-1">OCR:</span>
                        <span className={`font-medium ${
                          note.ocr_confidence > 80 ? 'text-green-600' :
                          note.ocr_confidence > 60 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {note.ocr_confidence}%
                        </span>
                      </div>
                    )}
                    {note.tags?.length > 0 && (
                      <div className="flex items-center">
                        <Tag className="h-3 w-3 mr-1" />
                        {note.tags.length} tags
                      </div>
                    )}
                    {note.action_items?.length > 0 && (
                      <div className="flex items-center">
                        <span className="mr-1">Actions:</span>
                        <span className="font-medium text-blue-600">
                          {note.action_items.length}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="ml-4 flex-shrink-0">
                  <Link
                    to={`/notes/${note.id}`}
                    className="btn btn-secondary flex items-center"
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    View
                  </Link>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="card text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No notes found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchQuery || selectedCategory
                ? 'Try adjusting your search criteria'
                : 'Get started by capturing your first note'
              }
            </p>
            <div className="mt-6">
              <Link to="/capture" className="btn btn-primary">
                Capture Note
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Pagination */}
      {notes && notes.total > pageSize && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, notes.total)} of {notes.total} notes
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="btn btn-secondary disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage(prev => prev + 1)}
              disabled={currentPage * pageSize >= notes.total}
              className="btn btn-secondary disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};