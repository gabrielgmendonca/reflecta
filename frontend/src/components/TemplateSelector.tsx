import { useState, useEffect } from 'react';
import { Layout, Columns } from 'lucide-react';
import type { Template } from '../types';
import { api } from '../api/client';
import { cn } from '../lib/utils';

interface TemplateSelectorProps {
  onSelect: (templateId: number | null) => void;
  selectedId: number | null;
}

export function TemplateSelector({ onSelect, selectedId }: TemplateSelectorProps) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTemplates().then((data) => {
      setTemplates(data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div className="text-gray-500">Loading templates...</div>;
  }

  return (
    <div className="grid gap-3">
      <button
        onClick={() => onSelect(null)}
        className={cn(
          'flex items-start gap-3 p-4 rounded-lg border-2 text-left transition-all',
          selectedId === null
            ? 'border-indigo-500 bg-indigo-50'
            : 'border-gray-200 hover:border-gray-300'
        )}
      >
        <Columns className="w-6 h-6 text-gray-500 mt-0.5" />
        <div>
          <div className="font-medium text-gray-900">Blank Board</div>
          <div className="text-sm text-gray-500">
            Start with default Start/Stop/Continue columns
          </div>
        </div>
      </button>

      {templates.map((template) => (
        <button
          key={template.id}
          onClick={() => onSelect(template.id)}
          className={cn(
            'flex items-start gap-3 p-4 rounded-lg border-2 text-left transition-all',
            selectedId === template.id
              ? 'border-indigo-500 bg-indigo-50'
              : 'border-gray-200 hover:border-gray-300'
          )}
        >
          <Layout className="w-6 h-6 text-gray-500 mt-0.5" />
          <div>
            <div className="font-medium text-gray-900">{template.name}</div>
            <div className="text-sm text-gray-500">{template.description}</div>
            <div className="flex gap-2 mt-2">
              {template.columns.map((col, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded text-xs text-white"
                  style={{ backgroundColor: col.color }}
                >
                  {col.title}
                </span>
              ))}
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}
