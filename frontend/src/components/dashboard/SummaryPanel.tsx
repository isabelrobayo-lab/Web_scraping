/**
 * SummaryPanel — Totals by Sitio_Origen and Operacion.
 *
 * Displays total active records, counts by site and operation,
 * and last successful task timestamp. (Req 10.4)
 */

import { useQuery } from '@tanstack/react-query';

import { get } from '@/api/client';
import type { SummaryResponse } from '@/types';

export function SummaryPanel() {
  const { data, isLoading } = useQuery({
    queryKey: ['summary'],
    queryFn: () => get<SummaryResponse>('/summary'),
  });

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Cargando resumen…</p>;
  }

  if (!data) return null;

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div className="rounded-md border p-4">
        <p className="text-xs font-medium text-muted-foreground">Registros Activos</p>
        <p className="mt-1 text-2xl font-bold">{data.total_active.toLocaleString()}</p>
      </div>

      <div className="rounded-md border p-4">
        <p className="text-xs font-medium text-muted-foreground">Última Ejecución Exitosa</p>
        <p className="mt-1 text-sm">
          {data.last_successful_task
            ? new Date(data.last_successful_task).toLocaleString()
            : '—'}
        </p>
      </div>

      <div className="rounded-md border p-4">
        <p className="text-xs font-medium text-muted-foreground mb-2">Por Sitio Origen</p>
        {data.by_sitio_origen.length === 0 ? (
          <p className="text-sm text-muted-foreground">Sin datos</p>
        ) : (
          <ul className="space-y-1">
            {data.by_sitio_origen.map((item) => (
              <li key={item.value} className="flex justify-between text-sm">
                <span className="truncate">{item.value}</span>
                <span className="font-medium">{item.count.toLocaleString()}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="rounded-md border p-4">
        <p className="text-xs font-medium text-muted-foreground mb-2">Por Operación</p>
        {data.by_operacion.length === 0 ? (
          <p className="text-sm text-muted-foreground">Sin datos</p>
        ) : (
          <ul className="space-y-1">
            {data.by_operacion.map((item) => (
              <li key={item.value} className="flex justify-between text-sm">
                <span>{item.value}</span>
                <span className="font-medium">{item.count.toLocaleString()}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
