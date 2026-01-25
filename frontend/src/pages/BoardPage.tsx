import { useParams } from 'react-router-dom';
import { Board } from '../components/Board';
import { BoardProvider } from '../context/BoardContext';

export function BoardPage() {
  const { slug } = useParams<{ slug: string }>();

  if (!slug) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-gray-600">Invalid board URL</div>
      </div>
    );
  }

  return (
    <BoardProvider slug={slug}>
      <Board />
    </BoardProvider>
  );
}
