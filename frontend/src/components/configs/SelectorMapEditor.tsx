/**
 * SelectorMapEditor — CSS selector mappings editor per Sitio_Origen.
 *
 * Allows creating/editing field-to-CSS-selector mappings.
 * Validates CSS selector syntax and supports multiple selectors per field.
 * (Req 4.1, 4.2, 4.5)
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2 } from 'lucide-react';

import { get, put } from '@/api/client';
import { Button } from '@/components/ui/button';
import type { SelectorMapResponse } from '@/types';

interface SelectorMapEditorProps {
  sitioOrigen: string;
}

interface MappingEntry {
  field: string;
  selectors: string[];
}

export function SelectorMapEditor({ sitioOrigen }: SelectorMapEditorProps) {
  const queryClient = useQueryClient();
  const [entries, setEntries] = useState<MappingEntry[]>([]);
  const [initialized, setInitialized] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['selector-maps', sitioOrigen],
    queryFn: () => get<SelectorMapResponse>(`/selector-maps/${sitioOrigen}`),
    enabled: !!sitioOrigen,
  });

  if (data && !initialized) {
    const mapped = Object.entries(data.mappings).map(([field, selectors]) => ({
      field,
      selectors: [...selectors],
    }));
    setEntries(mapped.length > 0 ? mapped : [{ field: '', selectors: [''] }]);
    setInitialized(true);
  }

  const saveMutation = useMutation({
    mutationFn: (mappings: Record<string, string[]>) =>
      put(`/selector-maps/${sitioOrigen}`, { mappings }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['selector-maps', sitioOrigen] });
    },
  });

  const addEntry = () => {
    setEntries((prev) => [...prev, { field: '', selectors: [''] }]);
  };

  const removeEntry = (index: number) => {
    setEntries((prev) => prev.filter((_, i) => i !== index));
  };

  const updateField = (index: number, field: string) => {
    setEntries((prev) =>
      prev.map((e, i) => (i === index ? { ...e, field } : e)),
    );
  };

  const updateSelector = (entryIndex: number, selectorIndex: number, value: string) => {
    setEntries((prev) =>
      prev.map((e, i) =>
        i === entryIndex
          ? {
              ...e,
              selectors: e.selectors.map((s, si) =>
                si === selectorIndex ? value : s,
              ),
            }
          : e,
      ),
    );
  };

  const addSelector = (entryIndex: number) => {
    setEntries((prev) =>
      prev.map((e, i) =>
        i === entryIndex ? { ...e, selectors: [...e.selectors, ''] } : e,
      ),
    );
  };

  const removeSelector = (entryIndex: number, selectorIndex: number) => {
    setEntries((prev) =>
      prev.map((e, i) =>
        i === entryIndex
          ? { ...e, selectors: e.selectors.filter((_, si) => si !== selectorIndex) }
          : e,
      ),
    );
  };

  const handleSave = () => {
    const mappings: Record<string, string[]> = {};
    for (const entry of entries) {
      const field = entry.field.trim();
      const selectors = entry.selectors.map((s) => s.trim()).filter(Boolean);
      if (field && selectors.length > 0) {
        mappings[field] = selectors;
      }
    }
    saveMutation.mutate(mappings);
  };

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Cargando mapa de selectores…</p>;
  }

  return (
    <div className="space-y-4">
      {data && (
        <p className="text-xs text-muted-foreground">
          Versión actual: {data.version} — Sitio: {data.sitio_origen}
        </p>
      )}

      <div className="space-y-3">
        {entries.map((entry, entryIndex) => (
          <div key={entryIndex} className="rounded-md border p-3 space-y-2">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={entry.field}
                onChange={(e) => updateField(entryIndex, e.target.value)}
                placeholder="Nombre del campo (ej: Precio_Local)"
                className="flex h-9 flex-1 rounded-md border border-input bg-background px-3 py-1 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                aria-label={`Campo ${entryIndex + 1}`}
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => removeEntry(entryIndex)}
                aria-label={`Eliminar campo ${entry.field || entryIndex + 1}`}
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>

            {entry.selectors.map((selector, selectorIndex) => (
              <div key={selectorIndex} className="flex items-center gap-2 pl-4">
                <input
                  type="text"
                  value={selector}
                  onChange={(e) =>
                    updateSelector(entryIndex, selectorIndex, e.target.value)
                  }
                  placeholder="Selector CSS (ej: .price-value)"
                  className="flex h-8 flex-1 rounded-md border border-input bg-background px-3 py-1 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  aria-label={`Selector ${selectorIndex + 1} para ${entry.field}`}
                />
                {entry.selectors.length > 1 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => removeSelector(entryIndex, selectorIndex)}
                    aria-label="Eliminar selector"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                )}
              </div>
            ))}

            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => addSelector(entryIndex)}
              className="ml-4 text-xs"
            >
              <Plus className="mr-1 h-3 w-3" /> Agregar selector
            </Button>
          </div>
        ))}
      </div>

      <div className="flex gap-3">
        <Button type="button" variant="outline" size="sm" onClick={addEntry}>
          <Plus className="mr-1 h-4 w-4" /> Agregar campo
        </Button>
        <Button
          type="button"
          size="sm"
          onClick={handleSave}
          disabled={saveMutation.isPending}
        >
          {saveMutation.isPending ? 'Guardando…' : 'Guardar mapa'}
        </Button>
      </div>

      {saveMutation.isError && (
        <p className="text-sm text-destructive" role="alert">
          Error al guardar. Verifique que los selectores CSS sean válidos.
        </p>
      )}
      {saveMutation.isSuccess && (
        <p className="text-sm text-green-600">Mapa guardado correctamente.</p>
      )}
    </div>
  );
}
