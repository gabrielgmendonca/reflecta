import { LogIn, LogOut, LayoutDashboard } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { useAuth } from '../context/AuthContext';

export function UserMenu() {
  const navigate = useNavigate();
  const { user, isLoading, login, logout } = useAuth();

  if (isLoading) {
    return (
      <div className="w-8 h-8 rounded-full bg-gray-200 animate-pulse" />
    );
  }

  if (!user) {
    return (
      <button
        onClick={login}
        className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg transition-colors"
      >
        <LogIn className="w-4 h-4" />
        <span className="text-sm font-medium">Sign in with Google</span>
      </button>
    );
  }

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button className="flex items-center gap-2 p-1 rounded-full hover:bg-gray-100 transition-colors">
          {user.picture ? (
            <img
              src={user.picture}
              alt={user.name}
              className="w-8 h-8 rounded-full"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-white text-sm font-medium">
              {user.name.charAt(0).toUpperCase()}
            </div>
          )}
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="min-w-[200px] bg-white rounded-lg shadow-lg border border-gray-200 p-1 z-50"
          sideOffset={5}
          align="end"
        >
          <div className="px-3 py-2 border-b border-gray-100">
            <p className="text-sm font-medium text-gray-900">{user.name}</p>
            <p className="text-xs text-gray-500">{user.email}</p>
          </div>

          <DropdownMenu.Item
            className="flex items-center gap-2 px-3 py-2 text-sm cursor-pointer rounded-md hover:bg-gray-100 outline-none"
            onClick={() => navigate('/dashboard')}
          >
            <LayoutDashboard className="w-4 h-4" />
            My Boards
          </DropdownMenu.Item>

          <DropdownMenu.Item
            className="flex items-center gap-2 px-3 py-2 text-sm cursor-pointer rounded-md hover:bg-gray-100 outline-none text-red-600"
            onClick={logout}
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
