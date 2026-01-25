import { Play, Pause, RotateCcw, Clock } from 'lucide-react';
import { useBoard } from '../context/BoardContext';
import { useTimer } from '../hooks/useTimer';
import { cn } from '../lib/utils';

interface TimerProps {
  endTime: string | null;
  duration: number;
}

export function Timer({ endTime, duration }: TimerProps) {
  const { startTimer, stopTimer, resetTimer } = useBoard();
  const { timeLeft, isRunning, displayTime } = useTimer(endTime, duration);

  const isLowTime = timeLeft !== null && timeLeft <= 30 && timeLeft > 0;
  const isExpired = timeLeft === 0;

  return (
    <div className="flex items-center gap-3 bg-gray-100 rounded-lg px-4 py-2">
      <Clock className="w-5 h-5 text-gray-500" />
      <span
        className={cn(
          'font-mono text-xl font-semibold tabular-nums',
          isExpired && 'text-red-600 animate-pulse',
          isLowTime && !isExpired && 'text-orange-500'
        )}
      >
        {displayTime}
      </span>
      <div className="flex gap-1 ml-2">
        {isRunning ? (
          <button
            onClick={stopTimer}
            className="p-1.5 hover:bg-gray-200 rounded-md transition-colors"
            title="Pause timer"
          >
            <Pause className="w-4 h-4 text-gray-600" />
          </button>
        ) : (
          <button
            onClick={startTimer}
            className="p-1.5 hover:bg-gray-200 rounded-md transition-colors"
            title="Start timer"
          >
            <Play className="w-4 h-4 text-gray-600" />
          </button>
        )}
        <button
          onClick={resetTimer}
          className="p-1.5 hover:bg-gray-200 rounded-md transition-colors"
          title="Reset timer"
        >
          <RotateCcw className="w-4 h-4 text-gray-600" />
        </button>
      </div>
    </div>
  );
}
