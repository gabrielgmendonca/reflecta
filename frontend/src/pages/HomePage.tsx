import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { Logo } from '../components/Logo';
import { TemplateSelector } from '../components/TemplateSelector';
import { UserMenu } from '../components/UserMenu';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';

export function HomePage() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [title, setTitle] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreate = async () => {
    if (!title.trim()) {
      setError('Please enter a board title');
      return;
    }

    setCreating(true);
    setError(null);

    try {
      const board = await api.createBoard(title.trim(), selectedTemplate || undefined, token || undefined);
      navigate(`/board/${board.slug}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create board');
      setCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <header className="absolute top-0 right-0 p-4">
        <UserMenu />
      </header>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Logo className="w-12 h-12" />
              <h1 className="text-4xl font-bold text-gray-900">Reflecta</h1>
            </div>
            <p className="text-lg text-gray-600">
              Collaborative retrospectives for agile teams
            </p>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-xl font-semibold mb-6">Create a New Board</h2>

            <div className="space-y-6">
              <div>
                <label
                  htmlFor="title"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Board Title
                </label>
                <input
                  id="title"
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Sprint 42 Retrospective"
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-shadow"
                  onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Choose a Template
                </label>
                <TemplateSelector
                  selectedId={selectedTemplate}
                  onSelect={setSelectedTemplate}
                />
              </div>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                  {error}
                </div>
              )}

              <button
                onClick={handleCreate}
                disabled={creating}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-indigo-500 hover:bg-indigo-600 disabled:bg-indigo-300 text-white font-semibold rounded-lg transition-colors"
              >
                {creating ? (
                  'Creating...'
                ) : (
                  <>
                    Create Board
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="mt-8 text-center text-sm text-gray-500">
            <p>Share the board URL with your team to collaborate in real-time</p>
          </div>
        </div>
      </div>
    </div>
  );
}
