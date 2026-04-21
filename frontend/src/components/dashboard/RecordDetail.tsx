/**
 * RecordDetail — Shows all 66 fields of a property record.
 *
 * Displays fields grouped by category for readability. (Req 10.5)
 */

import type { PropertyDetail } from '@/types';

interface RecordDetailProps {
  record: PropertyDetail;
}

interface FieldGroup {
  title: string;
  fields: { key: keyof PropertyDetail; label: string }[];
}

const FIELD_GROUPS: FieldGroup[] = [
  {
    title: 'Identificación',
    fields: [
      { key: 'id_interno', label: 'ID Interno' },
      { key: 'codigo_inmueble', label: 'Código Inmueble' },
      { key: 'sitio_origen', label: 'Sitio Origen' },
      { key: 'tipo_inmueble', label: 'Tipo Inmueble' },
      { key: 'operacion', label: 'Operación' },
      { key: 'titulo_anuncio', label: 'Título Anuncio' },
    ],
  },
  {
    title: 'Características',
    fields: [
      { key: 'habitaciones', label: 'Habitaciones' },
      { key: 'banos', label: 'Baños' },
      { key: 'estacionamiento', label: 'Estacionamiento' },
      { key: 'metros_utiles', label: 'Metros Útiles' },
      { key: 'metros_totales', label: 'Metros Totales' },
      { key: 'area_privada', label: 'Área Privada' },
      { key: 'area_construida', label: 'Área Construida' },
      { key: 'piso_propiedad', label: 'Piso' },
      { key: 'orientacion', label: 'Orientación' },
      { key: 'antiguedad_detalle', label: 'Antigüedad' },
      { key: 'rango_antiguedad', label: 'Rango Antigüedad' },
      { key: 'tipo_estudio', label: 'Tipo Estudio' },
      { key: 'es_loft', label: 'Es Loft' },
      { key: 'amoblado', label: 'Amoblado' },
    ],
  },
  {
    title: 'Ubicación',
    fields: [
      { key: 'municipio', label: 'Municipio' },
      { key: 'sector', label: 'Sector' },
      { key: 'barrio', label: 'Barrio' },
      { key: 'direccion', label: 'Dirección' },
      { key: 'estrato', label: 'Estrato' },
      { key: 'latitud', label: 'Latitud' },
      { key: 'longitud', label: 'Longitud' },
    ],
  },
  {
    title: 'Precios',
    fields: [
      { key: 'precio_local', label: 'Precio Local' },
      { key: 'precio_usd', label: 'Precio USD' },
      { key: 'simbolo_moneda', label: 'Moneda' },
      { key: 'administracion_valor', label: 'Administración' },
      { key: 'glosa_administracion', label: 'Glosa Administración' },
      { key: 'cambio_precio_valor', label: 'Cambio Precio' },
      { key: 'precio_bajo', label: 'Precio Bajo' },
    ],
  },
  {
    title: 'Contacto',
    fields: [
      { key: 'dueno_anuncio', label: 'Dueño Anuncio' },
      { key: 'telefono_principal', label: 'Teléfono Principal' },
      { key: 'telefono_opcional', label: 'Teléfono Opcional' },
      { key: 'correo_contacto', label: 'Correo' },
      { key: 'tipo_publicador', label: 'Tipo Publicador' },
      { key: 'tipo_empresa', label: 'Tipo Empresa' },
    ],
  },
  {
    title: 'Amenidades',
    fields: [
      { key: 'tiene_ascensores', label: 'Ascensores' },
      { key: 'tiene_balcones', label: 'Balcones' },
      { key: 'tiene_seguridad', label: 'Seguridad' },
      { key: 'tiene_bodega_deposito', label: 'Bodega/Depósito' },
      { key: 'tiene_terraza', label: 'Terraza' },
      { key: 'cuarto_servicio', label: 'Cuarto Servicio' },
      { key: 'bano_servicio', label: 'Baño Servicio' },
      { key: 'tiene_calefaccion', label: 'Calefacción' },
      { key: 'tiene_alarma', label: 'Alarma' },
      { key: 'acceso_controlado', label: 'Acceso Controlado' },
      { key: 'circuito_cerrado', label: 'Circuito Cerrado' },
      { key: 'estacionamiento_visita', label: 'Estac. Visita' },
      { key: 'cocina_americana', label: 'Cocina Americana' },
      { key: 'tiene_gimnasio', label: 'Gimnasio' },
      { key: 'tiene_bbq', label: 'BBQ' },
      { key: 'tiene_piscina', label: 'Piscina' },
      { key: 'en_conjunto_residencial', label: 'Conjunto Residencial' },
      { key: 'uso_comercial', label: 'Uso Comercial' },
    ],
  },
  {
    title: 'Estado y Fechas',
    fields: [
      { key: 'estado_activo', label: 'Estado Activo' },
      { key: 'fecha_control', label: 'Fecha Control' },
      { key: 'fecha_actualizacion', label: 'Fecha Actualización' },
      { key: 'fecha_publicacion', label: 'Fecha Publicación' },
      { key: 'fecha_desactivacion', label: 'Fecha Desactivación' },
    ],
  },
  {
    title: 'Enlaces',
    fields: [
      { key: 'url_anuncio', label: 'URL Anuncio' },
      { key: 'url_imagen_principal', label: 'URL Imagen' },
    ],
  },
  {
    title: 'Descripción',
    fields: [
      { key: 'descripcion_anuncio', label: 'Descripción' },
    ],
  },
];

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'boolean') return value ? 'Sí' : 'No';
  if (typeof value === 'number') return value.toLocaleString();
  return String(value);
}

export function RecordDetail({ record }: RecordDetailProps) {
  return (
    <div className="space-y-6">
      {FIELD_GROUPS.map((group) => (
        <section key={group.title}>
          <h3 className="mb-2 text-sm font-semibold text-muted-foreground uppercase tracking-wide">
            {group.title}
          </h3>
          <dl className="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2 lg:grid-cols-3">
            {group.fields.map(({ key, label }) => (
              <div key={key} className="flex flex-col">
                <dt className="text-xs text-muted-foreground">{label}</dt>
                <dd className="text-sm break-all">
                  {key === 'url_anuncio' || key === 'url_imagen_principal' ? (
                    record[key] ? (
                      <a href={String(record[key])} target="_blank" rel="noopener noreferrer" className="text-primary underline">
                        {String(record[key])}
                      </a>
                    ) : '—'
                  ) : formatValue(record[key])}
                </dd>
              </div>
            ))}
          </dl>
        </section>
      ))}
    </div>
  );
}
