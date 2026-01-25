import { useState, useRef, useEffect } from 'react';
import { Draggable } from '@hello-pangea/dnd';
import { ThumbsUp, Trash2, Edit2, Check, X } from 'lucide-react';
import type { Card as CardType } from '../types';
import { useBoard } from '../context/BoardContext';
import { cn } from '../lib/utils';

interface CardProps {
  card: CardType;
  index: number;
}

export function Card({ card, index }: CardProps) {
  const { sessionId, toggleVote, updateCard, deleteCard } = useBoard();
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(card.content);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const hasVoted = card.votes?.some((v) => v.session_id === sessionId) ?? false;
  const isOwner = card.session_id === sessionId;

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.select();
    }
  }, [isEditing]);

  const handleSave = () => {
    if (editContent.trim() && editContent !== card.content) {
      updateCard(card.id, { content: editContent.trim() });
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditContent(card.content);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  return (
    <Draggable draggableId={`card-${card.id}`} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={cn(
            'rounded-lg p-3 shadow-sm border border-gray-200 mb-2 transition-shadow',
            snapshot.isDragging && 'shadow-lg ring-2 ring-indigo-400'
          )}
          style={{
            ...provided.draggableProps.style,
            backgroundColor: card.color,
          }}
        >
          {isEditing ? (
            <div>
              <textarea
                ref={textareaRef}
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                onKeyDown={handleKeyDown}
                className="w-full p-1 rounded border border-gray-300 resize-none text-sm bg-white/80"
                rows={3}
              />
              <div className="flex justify-end gap-1 mt-1">
                <button
                  onClick={handleCancel}
                  className="p-1 hover:bg-black/10 rounded"
                  title="Cancel"
                >
                  <X className="w-4 h-4" />
                </button>
                <button
                  onClick={handleSave}
                  className="p-1 hover:bg-black/10 rounded"
                  title="Save"
                >
                  <Check className="w-4 h-4" />
                </button>
              </div>
            </div>
          ) : (
            <>
              <p className="text-sm text-gray-800 whitespace-pre-wrap break-words">
                {card.content}
              </p>
              <div className="flex items-center justify-between mt-2 pt-2 border-t border-black/10">
                <button
                  onClick={() => toggleVote(card.id)}
                  className={cn(
                    'flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors',
                    hasVoted
                      ? 'bg-indigo-500 text-white'
                      : 'bg-black/10 text-gray-700 hover:bg-black/20'
                  )}
                >
                  <ThumbsUp className="w-3 h-3" />
                  <span>{card.vote_count}</span>
                </button>
                {isOwner && (
                  <div className="flex gap-1">
                    <button
                      onClick={() => setIsEditing(true)}
                      className="p-1 hover:bg-black/10 rounded text-gray-600"
                      title="Edit"
                    >
                      <Edit2 className="w-3 h-3" />
                    </button>
                    <button
                      onClick={() => deleteCard(card.id)}
                      className="p-1 hover:bg-black/10 rounded text-gray-600"
                      title="Delete"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </Draggable>
  );
}
