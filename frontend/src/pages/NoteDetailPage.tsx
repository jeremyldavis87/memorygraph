import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { ArrowLeft, Calendar, Tag, FileText, Image, Download } from 'lucide-react';
import { notesService } from '../services/notesService.ts';

export const NoteDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const noteId = parseInt(id || '0', 10);

  const { data: note, isLoading, error } = useQuery(
    ['note', noteId],
    () => notesService.getNote(noteId),
    {
      enabled: !!noteId,
    }
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !note) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Note not found</h3>
          <p className="mt-1 text-sm text-gray-500">
            The note you're looking for doesn't exist or has been deleted.
          </p>
          <div className="mt-6">
            <Link to="/notes" className="btn btn-primary">
              Back to Notes
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/notes"
            className="btn btn-secondary flex items-center"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Notes
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{note.title}</h1>
            <div className="flex items-center space-x-4 mt-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                {note.source_type}
              </span>
              {note.ocr_confidence && (
                <span className="text-sm text-gray-600">
                  OCR Confidence: {note.ocr_confidence}%
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Summary */}
          {note.summary && (
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-3">Summary</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{note.summary}</p>
            </div>
          )}

          {/* Content */}
          {note.content && (
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-3">Content</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{note.content}</p>
              </div>
            </div>
          )}

          {/* Original Text */}
          {note.original_text && note.original_text !== note.content && (
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-3">Original Text</h2>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-700 whitespace-pre-wrap text-sm font-mono">
                  {note.original_text}
                </p>
              </div>
            </div>
          )}

          {/* Action Items */}
          {note.action_items && note.action_items.length > 0 && (
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-3">Action Items</h2>
              <ul className="space-y-2">
                {note.action_items.map((item: any, index: number) => (
                  <li key={index} className="flex items-start">
                    <span className={`inline-block w-4 h-4 rounded border mr-3 mt-0.5 ${
                      item.completed ? 'bg-green-500 border-green-500' : 'border-gray-300'
                    }`}>
                      {item.completed && (
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </span>
                    <span className={`${item.completed ? 'line-through text-gray-500' : 'text-gray-700'}`}>
                      {item.text}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Tags */}
          {note.tags && note.tags.length > 0 && (
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-3">Tags</h2>
              <div className="flex flex-wrap gap-2">
                {note.tags.map((tag: any, index: number) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                  >
                    <Tag className="h-3 w-3 mr-1" />
                    {tag.name || tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Metadata */}
          <div className="card">
            <h2 className="text-lg font-medium text-gray-900 mb-3">Details</h2>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Created</dt>
                <dd className="text-sm text-gray-900 flex items-center">
                  <Calendar className="h-4 w-4 mr-1" />
                  {formatDate(note.created_at)}
                </dd>
              </div>
              {note.updated_at && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Updated</dt>
                  <dd className="text-sm text-gray-900 flex items-center">
                    <Calendar className="h-4 w-4 mr-1" />
                    {formatDate(note.updated_at)}
                  </dd>
                </div>
              )}
              <div>
                <dt className="text-sm font-medium text-gray-500">OCR Mode</dt>
                <dd className="text-sm text-gray-900">{note.ocr_mode}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Processing Status</dt>
                <dd className="text-sm text-gray-900 capitalize">{note.processing_status}</dd>
              </div>
            </dl>
          </div>

          {/* Files */}
          {(note.file_path || note.image_path) && (
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-3">Files</h2>
              <div className="space-y-2">
                {note.image_path && (
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center">
                      <Image className="h-4 w-4 mr-2 text-gray-500" />
                      <span className="text-sm text-gray-700">Original Image</span>
                    </div>
                    <a
                      href={`http://localhost:8001/${note.image_path}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-sm btn-secondary flex items-center"
                    >
                      <Download className="h-3 w-3 mr-1" />
                      View
                    </a>
                  </div>
                )}
                {note.file_path && note.file_path !== note.image_path && (
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center">
                      <FileText className="h-4 w-4 mr-2 text-gray-500" />
                      <span className="text-sm text-gray-700">Original File</span>
                    </div>
                    <a
                      href={`http://localhost:8001/${note.file_path}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-sm btn-secondary flex items-center"
                    >
                      <Download className="h-3 w-3 mr-1" />
                      Download
                    </a>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Entities */}
          {note.entities && note.entities.length > 0 && (
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-3">Entities</h2>
              <div className="space-y-2">
                {note.entities.map((entity: any, index: number) => (
                  <div key={index} className="p-2 bg-gray-50 rounded">
                    <div className="text-sm font-medium text-gray-900">
                      {entity.name || entity.text}
                    </div>
                    {entity.type && (
                      <div className="text-xs text-gray-500">{entity.type}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
