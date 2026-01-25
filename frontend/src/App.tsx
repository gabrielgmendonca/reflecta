import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { HomePage } from './pages/HomePage';
import { BoardPage } from './pages/BoardPage';
import { DashboardPage } from './pages/DashboardPage';
import { AuthCallbackPage } from './pages/AuthCallbackPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/board/:slug" element={<BoardPage />} />
          <Route path="/auth/callback" element={<AuthCallbackPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
