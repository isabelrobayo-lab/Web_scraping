/**
 * FilterPanel — Combinable filters for property search.
 *
 * Supports: Sitio_Origen, Tipo_Inmueble, Operacion, Municipio, Sector,
 * Barrio, Estrato, precio range, metros range, Estado_Activo, Fecha_Control range.
 * (Req 10.1)
 */

import { useState } from 'react';
import { Search, X } from 'lucide-react';

import { Button } from '@/components/ui/button';
import type { PropertyFilters } from '@/types';

interface FilterPanelProps {
  filters: PropertyFilters;
  onApply: (filters: PropertyFilters) => void;
}

export function FilterPanel({ filters, onApply }: FilterPanelProps) {
  const [local, setLocal] = useState<PropertyFilters>(filters);

  const update = (key: keyof PropertyFilters, value: string | number | boolean | undefined) => {
    setLocal((prev) => ({ ...prev, [key]: value || undefined }));
  };

  const handleApply = (e: React.FormEvent) => {
    e.preventDefault();
    onApply(local);
  };

  const handleClear = () => {
    const empty: PropertyFilters = {};
    setLocal(empty);
    onApply(empty);
  };

  const inputClass =
    'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring';

  return (
    <form onSubmit={handleApply} className="space-y-4 rounded-md border p-4">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
        <div className="space-y-1">
          <label htmlFor="filter-sitio" className="text-xs font-medium">Sitio Origen</label>
          <input id="filter-sitio" className={inputClass} value={local.sitio_origen ?? ''} onChange={(e) => update('sitio_origen', e.target.value)} placeholder="ej: metrocuadrado" />
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-tipo" className="text-xs font-medium">Tipo Inmueble</label>
          <input id="filter-tipo" className={inputClass} value={local.tipo_inmueble ?? ''} onChange={(e) => update('tipo_inmueble', e.target.value)} placeholder="ej: Apartamento" />
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-operacion" className="text-xs font-medium">Operación</label>
          <select id="filter-operacion" className={inputClass} value={local.operacion ?? ''} onChange={(e) => update('operacion', e.target.value)}>
            <option value="">Todas</option>
            <option value="Venta">Venta</option>
            <option value="Arriendo">Arriendo</option>
          </select>
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-municipio" className="text-xs font-medium">Municipio</label>
          <input id="filter-municipio" className={inputClass} value={local.municipio ?? ''} onChange={(e) => update('municipio', e.target.value)} />
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-sector" className="text-xs font-medium">Sector</label>
          <input id="filter-sector" className={inputClass} value={local.sector ?? ''} onChange={(e) => update('sector', e.target.value)} />
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-barrio" className="text-xs font-medium">Barrio</label>
          <input id="filter-barrio" className={inputClass} value={local.barrio ?? ''} onChange={(e) => update('barrio', e.target.value)} />
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-estrato" className="text-xs font-medium">Estrato</label>
          <input id="filter-estrato" type="number" min={1} max={6} className={inputClass} value={local.estrato ?? ''} onChange={(e) => update('estrato', e.target.value ? Number(e.target.value) : undefined)} />
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-estado" className="text-xs font-medium">Estado Activo</label>
          <select id="filter-estado" className={inputClass} value={local.estado_activo === undefined ? '' : String(local.estado_activo)} onChange={(e) => update('estado_activo', e.target.value === '' ? undefined : e.target.value === 'true')}>
            <option value="">Todos</option>
            <option value="true">Activo</option>
            <option value="false">Inactivo</option>
          </select>
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-precio-min" className="text-xs font-medium">Precio mín.</label>
          <input id="filter-precio-min" type="number" className={inputClass} value={local.precio_min ?? ''} onChange={(e) => update('precio_min', e.target.value ? Number(e.target.value) : undefined)} />
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-precio-max" className="text-xs font-medium">Precio máx.</label>
          <input id="filter-precio-max" type="number" className={inputClass} value={local.precio_max ?? ''} onChange={(e) => update('precio_max', e.target.value ? Number(e.target.value) : undefined)} />
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-metros-min" className="text-xs font-medium">Metros mín.</label>
          <input id="filter-metros-min" type="number" className={inputClass} value={local.metros_min ?? ''} onChange={(e) => update('metros_min', e.target.value ? Number(e.target.value) : undefined)} />
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-metros-max" className="text-xs font-medium">Metros máx.</label>
          <input id="filter-metros-max" type="number" className={inputClass} value={local.metros_max ?? ''} onChange={(e) => update('metros_max', e.target.value ? Number(e.target.value) : undefined)} />
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-fecha-desde" className="text-xs font-medium">Fecha desde</label>
          <input id="filter-fecha-desde" type="date" className={inputClass} value={local.fecha_control_desde ?? ''} onChange={(e) => update('fecha_control_desde', e.target.value)} />
        </div>
        <div className="space-y-1">
          <label htmlFor="filter-fecha-hasta" className="text-xs font-medium">Fecha hasta</label>
          <input id="filter-fecha-hasta" type="date" className={inputClass} value={local.fecha_control_hasta ?? ''} onChange={(e) => update('fecha_control_hasta', e.target.value)} />
        </div>
      </div>
      <div className="flex gap-2">
        <Button type="submit" size="sm">
          <Search className="mr-1 h-4 w-4" /> Buscar
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={handleClear}>
          <X className="mr-1 h-4 w-4" /> Limpiar
        </Button>
      </div>
    </form>
  );
}
