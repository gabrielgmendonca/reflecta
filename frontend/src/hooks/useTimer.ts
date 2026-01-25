import { useState, useEffect, useMemo } from 'react';

function formatSeconds(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function useTimer(endTime: string | null, duration: number) {
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    if (!endTime) {
      setTimeLeft(null);
      setIsRunning(false);
      return;
    }

    const end = new Date(endTime).getTime();
    setIsRunning(true);

    const updateTimer = () => {
      const now = Date.now();
      const remaining = Math.max(0, Math.floor((end - now) / 1000));
      setTimeLeft(remaining);

      if (remaining <= 0) {
        setIsRunning(false);
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);

    return () => clearInterval(interval);
  }, [endTime]);

  const displayTime = useMemo(() => {
    if (timeLeft === null) {
      return formatSeconds(duration);
    }
    return formatSeconds(timeLeft);
  }, [timeLeft, duration]);

  return { timeLeft, isRunning, displayTime };
}
