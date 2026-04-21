/**
 * Vitest unit tests for dashboard components.
 *
 * Tests Task 18.10: Component rendering and basic behavior.
 */

import { describe, it, expect } from 'vitest';

import { render, screen } from '@/test/test-utils';
import { FilterPanel } from '@/components/dashboard/FilterPanel';
import { RecordDetail } from '@/components/dashboard/RecordDetail';
import { TaskProgressBar } from '@/components/dashboard/TaskProgressBar';
import { WebSocketContext, type WebSocketContextValue } from '@/providers/WebSocketProvider';
import type { PropertyDetail } from '@/types';

// ---------------------------------------------------------------------------
// FilterPanel
// ---------------------------------------------------------------------------

describe('FilterPanel', () => {
  it('renders all filter inputs', () => {
    render(<FilterPanel filters={{}} onApply={() => {}} />);
    expect(screen.getByLabelText('Sitio Origen')).toBeInTheDocument();
    expect(screen.getByLabelText('Tipo Inmueble')).toBeInTheDocument();
    expect(screen.getByLabelText('Operación')).toBeInTheDocument();
    expect(screen.getByLabelText('Municipio')).toBeInTheDocument();
    expect(screen.getByLabelText('Estrato')).toBeInTheDocument();
    expect(screen.getByLabelText('Estado Activo')).toBeInTheDocument();
    expect(screen.getByLabelText('Precio mín.')).toBeInTheDocument();
    expect(screen.getByLabelText('Precio máx.')).toBeInTheDocument();
  });

  it('renders search and clear buttons', () => {
    render(<FilterPanel filters={{}} onApply={() => {}} />);
    expect(screen.getByText('Buscar')).toBeInTheDocument();
    expect(screen.getByText('Limpiar')).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// RecordDetail
// ---------------------------------------------------------------------------

const mockRecord: PropertyDetail = {
  id_interno: 1,
  codigo_inmueble: 'INM-001',
  sitio_origen: 'test-site',
  tipo_inmueble: 'Apartamento',
  operacion: 'Venta',
  municipio: 'Bogotá',
  sector: 'Chapinero',
  barrio: 'El Retiro',
  estrato: 5,
  precio_local: 500000000,
  precio_usd: 125000,
  metros_utiles: 80,
  metros_totales: 95,
  habitaciones: 3,
  banos: 2,
  estado_activo: true,
  fecha_control: '2024-01-15T10:00:00Z',
  titulo_anuncio: 'Apartamento en Chapinero',
  url_anuncio: 'https://example.com/listing/1',
  estacionamiento: 1,
  administracion_valor: 350000,
  antiguedad_detalle: '5 años',
  rango_antiguedad: '1-10',
  tipo_estudio: false,
  es_loft: false,
  dueno_anuncio: 'Inmobiliaria Test',
  telefono_principal: null,
  telefono_opcional: null,
  correo_contacto: null,
  tipo_publicador: 'Inmobiliaria',
  descripcion_anuncio: 'Hermoso apartamento',
  fecha_actualizacion: null,
  amoblado: false,
  orientacion: 'Norte',
  latitud: 4.65,
  longitud: -74.05,
  url_imagen_principal: null,
  fecha_publicacion: null,
  direccion: 'Calle 85 #15-30',
  fecha_desactivacion: null,
  simbolo_moneda: 'COP',
  piso_propiedad: 8,
  tiene_ascensores: true,
  tiene_balcones: true,
  tiene_seguridad: true,
  tiene_bodega_deposito: false,
  tiene_terraza: false,
  cuarto_servicio: false,
  bano_servicio: false,
  tiene_calefaccion: false,
  tiene_alarma: true,
  acceso_controlado: true,
  circuito_cerrado: true,
  estacionamiento_visita: true,
  cocina_americana: false,
  tiene_gimnasio: true,
  tiene_bbq: false,
  tiene_piscina: false,
  en_conjunto_residencial: true,
  uso_comercial: false,
  cambio_precio_valor: null,
  precio_bajo: null,
  tipo_empresa: null,
  glosa_administracion: null,
  area_privada: 75,
  area_construida: 90,
};

describe('RecordDetail', () => {
  it('renders identification fields', () => {
    render(<RecordDetail record={mockRecord} />);
    expect(screen.getByText('INM-001')).toBeInTheDocument();
    expect(screen.getByText('test-site')).toBeInTheDocument();
    expect(screen.getByText('Apartamento')).toBeInTheDocument();
  });

  it('renders location fields', () => {
    render(<RecordDetail record={mockRecord} />);
    expect(screen.getByText('Bogotá')).toBeInTheDocument();
    expect(screen.getByText('Chapinero')).toBeInTheDocument();
  });

  it('renders boolean fields as Sí/No', () => {
    render(<RecordDetail record={mockRecord} />);
    const siElements = screen.getAllByText('Sí');
    expect(siElements.length).toBeGreaterThan(0);
  });

  it('renders null fields as dash', () => {
    render(<RecordDetail record={mockRecord} />);
    const dashes = screen.getAllByText('—');
    expect(dashes.length).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// TaskProgressBar
// ---------------------------------------------------------------------------

describe('TaskProgressBar', () => {
  const mockWsContext: WebSocketContextValue = {
    subscribe: () => {},
    unsubscribe: () => {},
    isConnected: true,
  };

  it('renders progress indicator', () => {
    render(
      <WebSocketContext.Provider value={mockWsContext}>
        <TaskProgressBar taskId="test-task-123" />
      </WebSocketContext.Provider>,
    );
    expect(screen.getByText('En progreso…')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows initial zero counts', () => {
    render(
      <WebSocketContext.Provider value={mockWsContext}>
        <TaskProgressBar taskId="test-task-123" />
      </WebSocketContext.Provider>,
    );
    expect(screen.getByText(/0 páginas/)).toBeInTheDocument();
    expect(screen.getByText(/0 registros/)).toBeInTheDocument();
  });
});
