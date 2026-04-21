/**
 * TaskMonitorDetail — Execution detail with counts and errors by type.
 *
 * Shows inserted/updated/skipped counts and errors grouped by type. (Req 13.2)
 */

import { useQuery } from '@tanstack/react-query';

import { get } from '@/api/client';
import type { TaskDetail } from '@/types';

interface TaskMonitorDetailProps {
  taskId: string;
}

export function TaskMonitorDetail({ taskId }: TaskMonitorDetailProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['task-detail', taskId],
    queryFn: () => get<TaskDetail>(`/tasks/${taskId}`),
    enabled: !!taskId,
  });

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Cargando detalle…</p>;
  }

  if (!data) return null;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Insertados" value={data.records_inserted} color="text-green-600" />
        <StatCard label="Actualizados" value={data.records_updated} color="text-blue-600" />
        <StatCard label="Omitidos" value={data.records_skipped} color="text-gray-600" />
        <StatCard label="Extraídos" value={data.records_extracted} />
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        <div className="rounded-md border p-3">
          <p className="text-xs text-muted-foreground">Estado</p>
          <p className="text-sm font-medium">{data.status}</p>
        </div>
        <div className="rounded-md border p-3">
          <p className="text-xs text-muted-foreground">Páginas procesadas</p>
          <p className="text-sm font-medium">{data.pages_processed}</p>
        </div>
        <div className="rounded-md border p-3">
          <p className="text-xs text-muted-foreground">Duración</p>
          <p className="text-sm font-medium">
            {data.duration_seconds != null ? `${data.duration_seconds.toFixed(1)}s` : '—'}
          </p>
        </div>
      </div>

      {data.correlation_id && (
        <p className="text-xs text-muted-foreground">
          Correlation ID: <span className="font-mono">{data.correlation_id}</span>
        </p>
      )}

      {data.errors_by_type && Object.keys(data.errors_by_type).length > 0 && (
        <div className="rounded-md border p-4">
          <h4 className="mb-2 text-sm font-medium">Errores por tipo</h4>
          <dl className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {Object.entries(data.errors_by_type).map(([type, count]) => (
              <div key={type}>
                <dt className="text-xs text-muted-foreground">{type}</dt>
                <dd className="text-lg font-bold text-destructive">{count}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number; color?: string }) {
  return (
    <div className="rounded-md border p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={`text-xl font-bold ${color ?? ''}`}>{value.toLocaleString()}</p>
    </div>
  );
}
