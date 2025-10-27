import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Search, FileText, User, Building, Calendar, Tag } from 'lucide-react';
import { searchService } from '../services/searchService';

export const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'notes' | 'entities'>('notes');

  const { data: searchResults, isLoading } = useQuery(
    ['search', query, searchType],
    () => searchService.search(query, searchType),
    {
      enabled: query.length > 2,
      refetchOnWindowFocus: false
    }
  );

  const { data: suggestions } = useQuery(
    ['suggestions', query],
    () => searchService.getSuggestions(query),
    {
      enabled: query.length > 0 && query.length <= 2,
      refetchOnWindowFocus: false
    }
  );

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
  };

  const getEntityIcon = (entityType: string) => {
    switch (entityType) {
      case 'person':
        return User;
      case 'organization':
        return Building;
      case 'project':
        return FileText;
      default:
        return Tag;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Search</h1>
        <p className="mt-1 text-sm text-gray-500">
          Find information across your knowledge base using natural language
        </p>
      </div>

      {/* Search Form */}
      <div className="card">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search for notes, people, projects, or concepts..."
                  className="input pl-10"
                />
              </div>
            </div>
            <div className="sm:w-48">
              <select
                value={searchType}
                onChange={(e) => setSearchType(e.target.value as 'notes' | 'entities')}
                className="input"
              >
                <option value="notes">Notes</option>
                <option value="entities">Entities</option>
              </select>
            </div>
            <button type="submit" className="btn btn-primary">
              Search
            </button>
          </div>
        </form>

        {/* Search Suggestions */}
        {suggestions?.suggestions?.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Suggestions:</h4>
            <div className="flex flex-wrap gap-2">
              {suggestions.suggestions.map((suggestion: any, index: number) => (
                <button
                  key={index}
                  onClick={() => setQuery(suggestion.text)}
                  className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
                >
                  {suggestion.text}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Search Results */}
      <div className="space-y-4">
        {query.length <= 2 ? (
          <div className="card text-center py-12">
            <Search className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Start typing to search</h3>
            <p className="mt-1 text-sm text-gray-500">
              Enter at least 3 characters to search your knowledge base
            </p>
          </div>
        ) : isLoading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : searchType === 'notes' ? (
          searchResults?.length ? (
            searchResults.map((note: any) => (
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
                      {note.tags && note.tags.length > 0 && (
                        <div className="flex items-center">
                          <Tag className="h-3 w-3 mr-1" />
                          {note.tags?.length} tags
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="card text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No notes found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try different search terms or check your spelling
              </p>
            </div>
          )
        ) : (
          searchResults?.length ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {searchResults.map((entity: any) => {
                const Icon = getEntityIcon(entity.entity_type);
                return (
                  <div key={entity.id} className="card hover:shadow-md transition-shadow">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                          <Icon className="h-5 w-5 text-primary-600" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-gray-900 truncate">
                          {entity.name}
                        </h3>
                        <p className="text-xs text-gray-500 capitalize">
                          {entity.entity_type}
                        </p>
                        {entity.description && (
                          <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                            {entity.description}
                          </p>
                        )}
                        <div className="mt-2 flex items-center text-xs text-gray-500">
                          <span>Mentioned {entity.mention_count} times</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="card text-center py-12">
              <Tag className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No entities found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try different search terms or check your spelling
              </p>
            </div>
          )
        )}
      </div>
    </div>
  );
};