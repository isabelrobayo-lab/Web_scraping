/**
 * ConfigList — Paginated table of scraping configurations.
 *
 * Displays URL, tipo_operacion, modo_ejecucion, estado_activo,
 * and last_execution_at. Provides edit, delete, and execute actions.
 * (Req 1.5)
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Pencil, Play, Trash2 } from 'lucide-react';

import { get, del, post } from '@/api/client';
import { useAuth } from '@/auth/useAuth';
import { Button } from '@/components/ui/button';
import { ConfirmDialog } from '@/components/shared/ConfirmDialog';
import { Pagination } from '@/components/shared/Pagination';
import type { ConfigResponse, PaginatedResponse } from '@/types';

interface ConfigListProps {
  onEdit?: (config: ConfigResponse) => void;
}

export function ConfigList({ onEdit }: ConfigListProps) {
  const [page, setPage] = useState(1);
  const [deleteTarget, setDeleteTarget] = useState<ConfigResponse | null>(null);
  const queryClient = useQueryClient();
  const { hasPermission } = useAuth();
  const canWrite = hasPermission('configs:write');
  const canExecute = hasPermission('tasks:execute');

  const { data, isLoading } = useQuery({
    queryKey: ['configs', page],
    queryFn: () =>
      get<PaginatedResponse<ConfigResponse>>('/configs', { page, per_page: 10 }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => del(`/configs/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configs'] });
      setDeleteTarget(null);
    },
  });

  const executeMutation = useMutation({
    mutationFn: (configId: number) => post(`/tasks/${configId}/execute`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Cargando configuraciones…</p>;
  }

  const configs = data?.items ?? [];

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto rounded-md border">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="px-4 py-3 text-left font-medium">URL</th>
              <th className="px-4 py-3 text-left font-medium">Operación</th>
              <th className="px-4 py-3 text-left font-medium">Modo</th>
              <th className="px-4 py-3 text-left font-medium">Activo</th>
              <th className="px-4 py-3 text-left font-medium">Última ejecución</th>
              <th className="px-4 py-3 text-right font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {configs.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                  No hay configuraciones registradas.
                </td>
              </tr>
            ) : (
              configs.map((config) => (
                <tr key={config.id} className="border-b hover:bg-muted/25">
                  <td className="max-w-xs truncate px-4 py-3" title={config.url_base}>
                    {config.url_base}
                  </td>
                  <td className="px-4 py-3">{config.tipo_operacion}</td>
                  <td className="px-4 py-3">{config.modo_ejecucion}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        config.active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {config.active ? 'Sí' : 'No'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {config.last_execution_at
                      ? new Date(config.last_execution_at).toLocaleString()
                      : '—'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-1">
                      {canWrite && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => onEdit?.(config)}
                          aria-label={`Editar ${config.url_base}`}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                      )}
                      {canExecute && config.active && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => executeMutation.mutate(config.id)}
                          disabled={executeMutation.isPending}
                          aria-label={`Ejecutar ${config.url_base}`}
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                      {canWrite && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setDeleteTarget(config)}
                          aria-label={`Eliminar ${config.url_base}`}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {data && (
        <Pagination
          page={data.page}
          pages={data.pages}
          total={data.total}
          onPageChange={setPage}
        />
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="Eliminar configuración"
        description={`¿Está seguro de desactivar la configuración para "${deleteTarget?.url_base}"? Esta acción marcará el registro como inactivo.`}
        confirmLabel="Desactivar"
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
