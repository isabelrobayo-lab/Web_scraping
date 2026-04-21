/**
 * TaskMonitorList — Paginated task list with filters.
 *
 * Filters: status, config, date, Sitio_Origen. (Req 13.1, 13.4)
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { get } from '@/api/client';
import { Pagination } from '@/components/shared/Pagination';
import type { TaskListItem, TaskFilters, PaginatedResponse } from '@/types';

interface TaskMonitorListProps {
  onSelect?: (task: TaskListItem) => void;
}

const STATUS_COLORS: Record<string, string> = {
  queued: 'bg-gray-100 text-gray-800',
  running: 'bg-blue-100 text-blue-800',
  success: 'bg-green-100 text-green-800',
  partial_success: 'bg-yellow-100 text-yellow-800',
  failure: 'bg-red-100 text-red-800',
};

export function TaskMonitorList({ onSelect }: TaskMonitorListProps) {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<TaskFilters>({});

  const { data, isLoading } = useQuery({
    queryKey: ['tasks', page, filters],
    queryFn: () => get<PaginatedResponse<TaskListItem>>('/tasks', { page, per_page: 15, ...filters }),
  });

  const inputClass = 'flex h-8 rounded-md border border-input bg-background px-2 py-1 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring';

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <select className={inputClass} value={filters.status ?? ''} onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value || undefined }))} aria-label="Filtrar por estado">
          <option value="">Todos los estados</option>
          <option value="queued">En cola</option>
          <option value="running">Ejecutando</option>
          <option value="success">Exitoso</option>
          <option value="partial_success">Parcial</option>
          <option value="failure">Fallido</option>
        </select>
        <input className={inputClass} placeholder="Sitio Origen" value={filters.sitio_origen ?? ''} onChange={(e) => setFilters((f) => ({ ...f, sitio_origen: e.target.value || undefined }))} aria-label="Filtrar por sitio origen" />
        <input type="date" className={inputClass} value={filters.fecha_desde ?? ''} onChange={(e) => setFilters((f) => ({ ...f, fecha_desde: e.target.value || undefined }))} aria-label="Fecha desde" />
        <input type="date" className={inputClass} value={filters.fecha_hasta ?? ''} onChange={(e) => setFilters((f) => ({ ...f, fecha_hasta: e.target.value || undefined }))} aria-label="Fecha hasta" />
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Cargando tareas…</p>
      ) : (
        <>
          <div className="overflow-x-auto rounded-md border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-3 py-2 text-left font-medium">ID</th>
                  <th className="px-3 py-2 text-left font-medium">Estado</th>
                  <th className="px-3 py-2 text-left font-medium">Inicio</th>
                  <th className="px-3 py-2 text-left font-medium">Duración</th>
                  <th className="px-3 py-2 text-right font-medium">Páginas</th>
                  <th className="px-3 py-2 text-right font-medium">Registros</th>
                </tr>
              </thead>
              <tbody>
                {(data?.items ?? []).length === 0 ? (
                  <tr><td colSpan={6} className="px-3 py-6 text-center text-muted-foreground">No se encontraron tareas.</td></tr>
                ) : (
                  data?.items.map((task) => (
                    <tr key={task.task_id} className="border-b hover:bg-muted/25 cursor-pointer" onClick={() => onSelect?.(task)} role="button" tabIndex={0} onKeyDown={(e) => e.key === 'Enter' && onSelect?.(task)}>
                      <td className="px-3 py-2 font-mono text-xs">{task.task_id.slice(0, 8)}</td>
                      <td className="px-3 py-2"><span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[task.status] ?? ''}`}>{task.status}</span></td>
                      <td className="px-3 py-2 text-muted-foreground">{task.started_at ? new Date(task.started_at).toLocaleString() : '—'}</td>
                      <td className="px-3 py-2">{task.duration_seconds != null ? `${task.duration_seconds.toFixed(1)}s` : '—'}</td>
                      <td className="px-3 py-2 text-right">{task.pages_processed}</td>
                      <td className="px-3 py-2 text-right">{task.records_extracted}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          {data && <Pagination page={data.page} pages={data.pages} total={data.total} onPageChange={setPage} />}
        </>
      )}
    </div>
  );
}
