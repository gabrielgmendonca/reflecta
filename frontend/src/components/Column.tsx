import { useState, useRef, useEffect } from 'react';
import { Droppable } from '@hello-pangea/dnd';
import { Plus } from 'lucide-react';
import type { Column as ColumnType } from '../types';
import { Card } from './Card';
import { useBoard } from '../context/BoardContext';
import { cn } from '../lib/utils';

interface ColumnProps {
  column: ColumnType;
}

export function Column({ column }: ColumnProps) {
  const { createCard } = useBoard();
  const [isAdding, setIsAdding] = useState(false);
  const [newContent, setNewContent] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isAdding && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isAdding]);

  const handleSubmit = () => {
    if (newContent.trim()) {
      createCard(column.id, newContent.trim());
      setNewContent('');
      setIsAdding(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    } else if (e.key === 'Escape') {
      setNewContent('');
      setIsAdding(false);
    }
  };

  // Sort cards by position
  const sortedCards = [...column.cards].sort((a, b) => a.position - b.position);

  return (
    <div className="flex-shrink-0 w-80 bg-gray-100 rounded-xl flex flex-col max-h-full">
      <div
        className="p-3 rounded-t-xl"
        style={{ backgroundColor: column.color }}
      >
        <h3 className="font-semibold text-white text-shadow">
          {column.title}
        </h3>
        <span className="text-xs text-white/80">
          {column.cards.length} card{column.cards.length !== 1 ? 's' : ''}
        </span>
      </div>

      <Droppable droppableId={`column-${column.id}`} type="CARD">
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={cn(
              'flex-1 p-2 overflow-y-auto min-h-[100px]',
              snapshot.isDraggingOver && 'bg-indigo-50'
            )}
          >
            {sortedCards.map((card, index) => (
              <Card key={card.id} card={card} index={index} />
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>

      <div className="p-2 border-t border-gray-200">
        {isAdding ? (
          <div className="space-y-2">
            <textarea
              ref={textareaRef}
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter card content..."
              className="w-full p-2 rounded-lg border border-gray-300 resize-none text-sm"
              rows={3}
            />
            <div className="flex gap-2">
              <button
                onClick={handleSubmit}
                className="flex-1 px-3 py-1 bg-indigo-500 text-white rounded-lg text-sm font-medium hover:bg-indigo-600"
              >
                Add
              </button>
              <button
                onClick={() => {
                  setNewContent('');
                  setIsAdding(false);
                }}
                className="px-3 py-1 text-gray-600 hover:bg-gray-200 rounded-lg text-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setIsAdding(true)}
            className="w-full flex items-center justify-center gap-1 px-3 py-2 text-gray-600 hover:bg-gray-200 rounded-lg text-sm font-medium transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Card
          </button>
        )}
      </div>
    </div>
  );
}
