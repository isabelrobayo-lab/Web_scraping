/**
 * ErrorLogViewer — Error log list with filters.
 *
 * Filters: error_type, Sitio_Origen, Tarea_Scraping, date range. (Req 10.6)
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { get } from '@/api/client';
import { Pagination } from '@/components/shared/Pagination';
import type { ErrorListItem, ErrorFilters, PaginatedResponse } from '@/types';

export function ErrorLogViewer() {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<ErrorFilters>({});

  const { data, isLoading } = useQuery({
    queryKey: ['errors', page, filters],
    queryFn: () =>
      get<PaginatedResponse<ErrorListItem>>('/errors', {
        page,
        per_page: 20,
        ...filters,
      }),
  });

  const inputClass =
    'flex h-8 rounded-md border border-input bg-background px-2 py-1 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring';

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <select
          className={inputClass}
          value={filters.error_type ?? ''}
          onChange={(e) => setFilters((f) => ({ ...f, error_type: e.target.value || undefined }))}
          aria-label="Filtrar por tipo de error"
        >
          <option value="">Todos los tipos</option>
          <option value="Timeout">Timeout</option>
          <option value="CAPTCHA">CAPTCHA</option>
          <option value="Estructura">Estructura</option>
          <option value="Conexion">Conexión</option>
        </select>
        <input className={inputClass} placeholder="Sitio Origen" value={filters.sitio_origen ?? ''} onChange={(e) => setFilters((f) => ({ ...f, sitio_origen: e.target.value || undefined }))} aria-label="Filtrar por sitio origen" />
        <input className={inputClass} placeholder="Task ID" value={filters.task_id ?? ''} onChange={(e) => setFilters((f) => ({ ...f, task_id: e.target.value || undefined }))} aria-label="Filtrar por tarea" />
        <input type="date" className={inputClass} value={filters.fecha_desde ?? ''} onChange={(e) => setFilters((f) => ({ ...f, fecha_desde: e.target.value || undefined }))} aria-label="Fecha desde" />
        <input type="date" className={inputClass} value={filters.fecha_hasta ?? ''} onChange={(e) => setFilters((f) => ({ ...f, fecha_hasta: e.target.value || undefined }))} aria-label="Fecha hasta" />
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Cargando errores…</p>
      ) : (
        <>
          <div className="overflow-x-auto rounded-md border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-3 py-2 text-left font-medium">Tipo</th>
                  <th className="px-3 py-2 text-left font-medium">Sitio</th>
                  <th className="px-3 py-2 text-left font-medium">URL</th>
                  <th className="px-3 py-2 text-left font-medium">Mensaje</th>
                  <th className="px-3 py-2 text-left font-medium">Fecha</th>
                </tr>
              </thead>
              <tbody>
                {(data?.items ?? []).length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-3 py-6 text-center text-muted-foreground">
                      No se encontraron errores.
                    </td>
                  </tr>
                ) : (
                  data?.items.map((err) => (
                    <tr key={err.id} className="border-b hover:bg-muted/25">
                      <td className="px-3 py-2">
                        <span className="inline-flex rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800">
                          {err.error_type}
                        </span>
                      </td>
                      <td className="px-3 py-2">{err.sitio_origen}</td>
                      <td className="max-w-xs truncate px-3 py-2" title={err.url ?? ''}>{err.url ?? '—'}</td>
                      <td className="max-w-xs truncate px-3 py-2" title={err.error_message ?? ''}>{err.error_message ?? '—'}</td>
                      <td className="px-3 py-2 text-muted-foreground">{new Date(err.created_at).toLocaleString()}</td>
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
