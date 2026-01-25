import { DragDropContext, type DropResult } from '@hello-pangea/dnd';
import { Column } from './Column';
import { Timer } from './Timer';
import { ShareButton } from './ShareButton';
import { ExportMenu } from './ExportMenu';
import { UserMenu } from './UserMenu';
import { useBoard } from '../context/BoardContext';

export function Board() {
  const { board, loading, error, moveCard, isConnected } = useBoard();

  const handleDragEnd = (result: DropResult) => {
    const { destination, source, draggableId } = result;

    if (!destination) return;

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const cardId = parseInt(draggableId.replace('card-', ''), 10);
    const columnId = parseInt(destination.droppableId.replace('column-', ''), 10);

    moveCard(cardId, columnId, destination.index);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-gray-600">Loading board...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-red-600">{error}</div>
      </div>
    );
  }

  if (!board) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-gray-600">Board not found</div>
      </div>
    );
  }

  // Sort columns by position
  const sortedColumns = [...board.columns].sort((a, b) => a.position - b.position);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-gray-800">{board.title}</h1>
            <div
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`}
              title={isConnected ? 'Connected' : 'Disconnected'}
            />
          </div>
          <div className="flex items-center gap-4">
            <Timer
              endTime={board.timer_end_time}
              duration={board.timer_duration}
            />
            <ShareButton />
            <ExportMenu slug={board.slug} />
            <UserMenu />
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-x-auto p-6">
        <DragDropContext onDragEnd={handleDragEnd}>
          <div className="flex gap-4 h-full">
            {sortedColumns.map((column) => (
              <Column key={column.id} column={column} />
            ))}
          </div>
        </DragDropContext>
      </main>
    </div>
  );
}
