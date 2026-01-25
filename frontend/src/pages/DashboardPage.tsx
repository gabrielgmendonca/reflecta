import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, Calendar, Users, MoreVertical, Trash2, ExternalLink } from 'lucide-react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { Logo } from '../components/Logo';
import { UserMenu } from '../components/UserMenu';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import type { Board } from '../types';

export function DashboardPage() {
  const navigate = useNavigate();
  const { user, token, isLoading: authLoading } = useAuth();
  const [boards, setBoards] = useState<Board[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/');
      return;
    }

    if (token) {
      loadBoards();
    }
  }, [token, authLoading, user, navigate]);

  const loadBoards = async () => {
    if (!token) return;

    setLoading(true);
    setError(null);
    try {
      const data = await api.getMyBoards(token);
      setBoards(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load boards');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (slug: string) => {
    if (!token) return;
    if (!confirm('Are you sure you want to delete this board?')) return;

    try {
      await api.deleteBoard(slug, token);
      setBoards(boards.filter(b => b.slug !== slug));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete board');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <Logo className="w-8 h-8" />
              <h1 className="text-xl font-bold text-gray-900">Reflecta</h1>
            </Link>
            <UserMenu />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">My Boards</h2>
            <p className="text-gray-600 mt-1">
              {boards.length} board{boards.length !== 1 ? 's' : ''}
            </p>
          </div>
          <Link
            to="/"
            className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            New Board
          </Link>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-600">{error}</p>
            <button
              onClick={loadBoards}
              className="mt-4 text-indigo-500 hover:underline"
            >
              Try again
            </button>
          </div>
        ) : boards.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No boards yet</h3>
            <p className="text-gray-500 mb-6">Create your first retrospective board to get started.</p>
            <Link
              to="/"
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg transition-colors"
            >
              <Plus className="w-5 h-5" />
              Create Board
            </Link>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {boards.map((board) => (
              <div
                key={board.id}
                className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <Link
                    to={`/board/${board.slug}`}
                    className="text-lg font-semibold text-gray-900 hover:text-indigo-600 transition-colors"
                  >
                    {board.title}
                  </Link>
                  <DropdownMenu.Root>
                    <DropdownMenu.Trigger asChild>
                      <button className="p-1 hover:bg-gray-100 rounded-md transition-colors">
                        <MoreVertical className="w-5 h-5 text-gray-400" />
                      </button>
                    </DropdownMenu.Trigger>
                    <DropdownMenu.Portal>
                      <DropdownMenu.Content
                        className="min-w-[140px] bg-white rounded-lg shadow-lg border border-gray-200 p-1 z-50"
                        sideOffset={5}
                        align="end"
                      >
                        <DropdownMenu.Item
                          className="flex items-center gap-2 px-3 py-2 text-sm cursor-pointer rounded-md hover:bg-gray-100 outline-none"
                          onClick={() => navigate(`/board/${board.slug}`)}
                        >
                          <ExternalLink className="w-4 h-4" />
                          Open
                        </DropdownMenu.Item>
                        <DropdownMenu.Item
                          className="flex items-center gap-2 px-3 py-2 text-sm cursor-pointer rounded-md hover:bg-gray-100 outline-none text-red-600"
                          onClick={() => handleDelete(board.slug)}
                        >
                          <Trash2 className="w-4 h-4" />
                          Delete
                        </DropdownMenu.Item>
                      </DropdownMenu.Content>
                    </DropdownMenu.Portal>
                  </DropdownMenu.Root>
                </div>

                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {formatDate(board.created_at)}
                  </div>
                  {board.columns && (
                    <div className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      {board.columns.reduce((acc, col) => acc + (col.cards?.length || 0), 0)} cards
                    </div>
                  )}
                </div>

                <Link
                  to={`/board/${board.slug}`}
                  className="mt-4 block w-full text-center py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition-colors"
                >
                  Open Board
                </Link>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
