/**
 * Zod validation schemas for scraping configuration forms.
 *
 * Mirrors backend Pydantic validation: URL format, depth 1-10,
 * cron required when modo_ejecucion is Programado.
 */

import { z } from 'zod';

const URL_PATTERN =
  /^https?:\/\/[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}(:\d{1,5})?(\/[^\s]*)?$/;

const CRON_PATTERN = /^(\S+\s+){4}\S+$/;

export const configCreateSchema = z
  .object({
    url_base: z
      .string()
      .min(1, 'La URL es requerida')
      .max(2048, 'La URL no puede exceder 2048 caracteres')
      .regex(URL_PATTERN, 'Debe ser una URL HTTP o HTTPS válida (ej: https://www.ejemplo.com)'),
    profundidad_navegacion: z
      .number({ invalid_type_error: 'La profundidad debe ser un número' })
      .int('La profundidad debe ser un número entero')
      .min(1, 'La profundidad mínima es 1')
      .max(10, 'La profundidad máxima es 10'),
    tipo_operacion: z.enum(['Venta', 'Arriendo'], {
      errorMap: () => ({ message: 'Seleccione Venta o Arriendo' }),
    }),
    modo_ejecucion: z.enum(['Manual', 'Programado'], {
      errorMap: () => ({ message: 'Seleccione Manual o Programado' }),
    }),
    cron_expression: z.string().nullable().optional(),
  })
  .refine(
    (data) => {
      if (data.modo_ejecucion === 'Programado') {
        return !!data.cron_expression && CRON_PATTERN.test(data.cron_expression);
      }
      return true;
    },
    {
      message: 'Se requiere una expresión cron válida cuando el modo es Programado (ej: 0 8 * * 1)',
      path: ['cron_expression'],
    },
  );

export const configUpdateSchema = z
  .object({
    url_base: z
      .string()
      .min(1, 'La URL es requerida')
      .max(2048, 'La URL no puede exceder 2048 caracteres')
      .regex(URL_PATTERN, 'Debe ser una URL HTTP o HTTPS válida')
      .optional(),
    profundidad_navegacion: z
      .number({ invalid_type_error: 'La profundidad debe ser un número' })
      .int('La profundidad debe ser un número entero')
      .min(1, 'La profundidad mínima es 1')
      .max(10, 'La profundidad máxima es 10')
      .optional(),
    tipo_operacion: z.enum(['Venta', 'Arriendo']).optional(),
    modo_ejecucion: z.enum(['Manual', 'Programado']).optional(),
    cron_expression: z.string().nullable().optional(),
  })
  .refine(
    (data) => {
      if (data.modo_ejecucion === 'Programado') {
        return !!data.cron_expression && CRON_PATTERN.test(data.cron_expression);
      }
      return true;
    },
    {
      message: 'Se requiere una expresión cron válida cuando el modo es Programado',
      path: ['cron_expression'],
    },
  );

export type ConfigCreateInput = z.infer<typeof configCreateSchema>;
export type ConfigUpdateInput = z.infer<typeof configUpdateSchema>;
