/**
 * TaskProgressBar — Real-time WebSocket progress updates.
 *
 * Displays page count and record count from task_progress messages. (Req 13.3)
 */

import { useState } from 'react';

import { useWebSocket } from '@/hooks/useWebSocket';

interface TaskProgressBarProps {
  taskId: string;
}

interface ProgressData {
  pages: number;
  records: number;
}

export function TaskProgressBar({ taskId }: TaskProgressBarProps) {
  const [progress, setProgress] = useState<ProgressData>({ pages: 0, records: 0 });
  const [isActive, setIsActive] = useState(true);

  useWebSocket('task_progress', (message) => {
    const payload = message.payload as { task_id?: string; pages?: number; records?: number };
    if (payload.task_id === taskId) {
      setProgress({
        pages: payload.pages ?? 0,
        records: payload.records ?? 0,
      });
    }
  });

  useWebSocket('task_status', (message) => {
    const payload = message.payload as { task_id?: string; status?: string };
    if (payload.task_id === taskId) {
      const terminal = ['success', 'partial_success', 'failure'];
      if (terminal.includes(payload.status ?? '')) {
        setIsActive(false);
      }
    }
  });

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>{isActive ? 'En progreso…' : 'Completado'}</span>
        <span>
          {progress.pages} páginas · {progress.records} registros
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            isActive ? 'bg-primary animate-pulse' : 'bg-green-500'
          }`}
          style={{ width: isActive ? '75%' : '100%' }}
          role="progressbar"
          aria-valuenow={progress.records}
          aria-label={`Progreso: ${progress.pages} páginas, ${progress.records} registros`}
        />
      </div>
    </div>
  );
}
