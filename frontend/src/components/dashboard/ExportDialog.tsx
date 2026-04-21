/**
 * ExportDialog — Format selection and async progress tracking.
 *
 * Allows selecting CSV, Excel, or JSON format. For large exports,
 * tracks async progress via polling. (Req 10.3, 10.7)
 */

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';

import { post, get } from '@/api/client';
import { Button } from '@/components/ui/button';
import type { ExportCreateResponse, ExportFormat, ExportStatusResponse, PropertyFilters } from '@/types';

interface ExportDialogProps {
  open: boolean;
  filters: PropertyFilters;
  onClose: () => void;
}

export function ExportDialog({ open, filters, onClose }: ExportDialogProps) {
  const [format, setFormat] = useState<ExportFormat>('csv');
  const [exportId, setExportId] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: () =>
      post<ExportCreateResponse>('/exports', { format, filters }),
    onSuccess: (data) => {
      setExportId(data.export_id);
    },
  });

  const { data: statusData } = useQuery({
    queryKey: ['export-status', exportId],
    queryFn: () => get<ExportStatusResponse>(`/exports/${exportId}/status`),
    enabled: !!exportId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'completed' || status === 'failed' ? false : 2000;
    },
  });

  const handleExport = () => {
    setExportId(null);
    createMutation.mutate();
  };

  const handleDownload = () => {
    if (exportId) {
      window.open(`/api/v1/exports/${exportId}/download`, '_blank');
    }
  };

  const handleClose = () => {
    setExportId(null);
    onClose();
  };

  if (!open) return null;

  const isCompleted = statusData?.status === 'completed';
  const isFailed = statusData?.status === 'failed';
  const isProcessing = exportId && !isCompleted && !isFailed;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" role="dialog" aria-modal="true" aria-labelledby="export-dialog-title" onClick={handleClose}>
      <div className="w-full max-w-sm rounded-lg border bg-background p-6 shadow-lg" onClick={(e) => e.stopPropagation()}>
        <h2 id="export-dialog-title" className="text-lg font-semibold">Exportar Datos</h2>

        {!exportId ? (
          <div className="mt-4 space-y-4">
            <div className="space-y-2">
              <label htmlFor="export-format" className="text-sm font-medium">Formato</label>
              <select id="export-format" className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" value={format} onChange={(e) => setFormat(e.target.value as ExportFormat)}>
                <option value="csv">CSV</option>
                <option value="excel">Excel</option>
                <option value="json">JSON</option>
              </select>
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={handleClose}>Cancelar</Button>
              <Button onClick={handleExport} disabled={createMutation.isPending}>{createMutation.isPending ? 'Iniciando…' : 'Exportar'}</Button>
            </div>
          </div>
        ) : (
          <div className="mt-4 space-y-4">
            {isProcessing && (
              <div className="space-y-2">
                <p className="text-sm">Generando exportación…</p>
                <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div className="h-full animate-pulse rounded-full bg-primary" style={{ width: '60%' }} />
                </div>
                {statusData && <p className="text-xs text-muted-foreground">{statusData.record_count.toLocaleString()} registros procesados</p>}
              </div>
            )}
            {isCompleted && (
              <div className="space-y-2">
                <p className="text-sm text-green-600">Exportación completada ({statusData.record_count.toLocaleString()} registros)</p>
                <Button onClick={handleDownload} className="w-full">Descargar archivo</Button>
              </div>
            )}
            {isFailed && <p className="text-sm text-destructive">Error al generar la exportación. Intente nuevamente.</p>}
            <div className="flex justify-end">
              <Button variant="outline" onClick={handleClose}>Cerrar</Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
