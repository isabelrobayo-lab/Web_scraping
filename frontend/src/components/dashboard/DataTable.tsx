/**
 * DataTable — Configurable columns table with pagination.
 *
 * Generic table component for displaying property records
 * with selectable visible columns. (Req 10.2)
 */

import { useState } from 'react';

import { Pagination } from '@/components/shared/Pagination';
import type { PropertyListItem, PaginatedResponse } from '@/types';

interface Column {
  key: keyof PropertyListItem;
  label: string;
  render?: (value: unknown, row: PropertyListItem) => React.ReactNode;
}

const DEFAULT_COLUMNS: Column[] = [
  { key: 'codigo_inmueble', label: 'Código' },
  { key: 'sitio_origen', label: 'Sitio' },
  { key: 'tipo_inmueble', label: 'Tipo' },
  { key: 'operacion', label: 'Operación' },
  { key: 'municipio', label: 'Municipio' },
  { key: 'precio_local', label: 'Precio', render: (v) => v != null ? Number(v).toLocaleString() : '—' },
  { key: 'metros_totales', label: 'Metros²', render: (v) => v != null ? String(v) : '—' },
  { key: 'habitaciones', label: 'Hab.' },
  { key: 'estado_activo', label: 'Activo', render: (v) => v === true ? 'Sí' : v === false ? 'No' : '—' },
];

interface DataTableProps {
  data: PaginatedResponse<PropertyListItem> | undefined;
  isLoading: boolean;
  page: number;
  onPageChange: (page: number) => void;
  onRowClick?: (item: PropertyListItem) => void;
  columns?: Column[];
}

export function DataTable({
  data,
  isLoading,
  page,
  onPageChange,
  onRowClick,
  columns = DEFAULT_COLUMNS,
}: DataTableProps) {
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(
    new Set(columns.map((c) => c.key)),
  );

  const toggleColumn = (key: string) => {
    setVisibleKeys((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        if (next.size > 1) next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const visibleColumns = columns.filter((c) => visibleKeys.has(c.key));

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Cargando datos…</p>;
  }

  const items = data?.items ?? [];

  return (
    <div className="space-y-4">
      <details className="text-xs">
        <summary className="cursor-pointer text-muted-foreground">Columnas visibles</summary>
        <div className="mt-2 flex flex-wrap gap-2">
          {columns.map((col) => (
            <label key={col.key} className="flex items-center gap-1">
              <input
                type="checkbox"
                checked={visibleKeys.has(col.key)}
                onChange={() => toggleColumn(col.key)}
                className="rounded"
              />
              <span>{col.label}</span>
            </label>
          ))}
        </div>
      </details>

      <div className="overflow-x-auto rounded-md border">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              {visibleColumns.map((col) => (
                <th key={col.key} className="px-4 py-3 text-left font-medium">
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={visibleColumns.length} className="px-4 py-8 text-center text-muted-foreground">
                  No se encontraron registros.
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr
                  key={item.id_interno}
                  className="border-b hover:bg-muted/25 cursor-pointer"
                  onClick={() => onRowClick?.(item)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => e.key === 'Enter' && onRowClick?.(item)}
                >
                  {visibleColumns.map((col) => (
                    <td key={col.key} className="px-4 py-3">
                      {col.render
                        ? col.render(item[col.key], item)
                        : (item[col.key] ?? '—')}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {data && (
        <Pagination
          page={page}
          pages={data.pages}
          total={data.total}
          onPageChange={onPageChange}
        />
      )}
    </div>
  );
}
