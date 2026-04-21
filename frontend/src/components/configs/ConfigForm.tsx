/**
 * ConfigForm — Create/edit scraping configuration form.
 *
 * Uses React Hook Form + Zod for validation.
 * URL, depth 1-10, cron required when Programado. (Req 1.1-1.4, 1.8)
 */

import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { post, put } from '@/api/client';
import { Button } from '@/components/ui/button';
import { CronScheduleInput } from '@/components/configs/CronScheduleInput';
import { configCreateSchema, type ConfigCreateInput } from '@/schemas/config';
import type { ConfigResponse } from '@/types';

interface ConfigFormProps {
  config?: ConfigResponse | null;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function ConfigForm({ config, onSuccess, onCancel }: ConfigFormProps) {
  const queryClient = useQueryClient();
  const isEditing = !!config;

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors },
  } = useForm<ConfigCreateInput>({
    resolver: zodResolver(configCreateSchema),
    defaultValues: {
      url_base: config?.url_base ?? '',
      profundidad_navegacion: config?.profundidad_navegacion ?? 1,
      tipo_operacion: (config?.tipo_operacion as 'Venta' | 'Arriendo') ?? 'Venta',
      modo_ejecucion: (config?.modo_ejecucion as 'Manual' | 'Programado') ?? 'Manual',
      cron_expression: config?.cron_expression ?? null,
    },
  });

  const modoEjecucion = watch('modo_ejecucion');

  const mutation = useMutation({
    mutationFn: (data: ConfigCreateInput) =>
      isEditing
        ? put(`/configs/${config.id}`, data)
        : post('/configs', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configs'] });
      onSuccess?.();
    },
  });

  const onSubmit = (data: ConfigCreateInput) => {
    if (data.modo_ejecucion === 'Manual') {
      data.cron_expression = null;
    }
    mutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-2">
        <label htmlFor="url_base" className="text-sm font-medium">
          URL Base
        </label>
        <input
          id="url_base"
          type="text"
          {...register('url_base')}
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          placeholder="https://www.ejemplo.com/inmuebles"
        />
        {errors.url_base && (
          <p className="text-sm text-destructive" role="alert">
            {errors.url_base.message}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <label htmlFor="profundidad_navegacion" className="text-sm font-medium">
          Profundidad de Navegación (1-10)
        </label>
        <input
          id="profundidad_navegacion"
          type="number"
          min={1}
          max={10}
          {...register('profundidad_navegacion', { valueAsNumber: true })}
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
        {errors.profundidad_navegacion && (
          <p className="text-sm text-destructive" role="alert">
            {errors.profundidad_navegacion.message}
          </p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label htmlFor="tipo_operacion" className="text-sm font-medium">
            Tipo de Operación
          </label>
          <select
            id="tipo_operacion"
            {...register('tipo_operacion')}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value="Venta">Venta</option>
            <option value="Arriendo">Arriendo</option>
          </select>
          {errors.tipo_operacion && (
            <p className="text-sm text-destructive" role="alert">
              {errors.tipo_operacion.message}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <label htmlFor="modo_ejecucion" className="text-sm font-medium">
            Modo de Ejecución
          </label>
          <select
            id="modo_ejecucion"
            {...register('modo_ejecucion')}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value="Manual">Manual</option>
            <option value="Programado">Programado</option>
          </select>
          {errors.modo_ejecucion && (
            <p className="text-sm text-destructive" role="alert">
              {errors.modo_ejecucion.message}
            </p>
          )}
        </div>
      </div>

      {modoEjecucion === 'Programado' && (
        <Controller
          name="cron_expression"
          control={control}
          render={({ field }) => (
            <CronScheduleInput
              value={field.value ?? ''}
              onChange={field.onChange}
              error={errors.cron_expression?.message}
            />
          )}
        />
      )}

      {mutation.isError && (
        <p className="text-sm text-destructive" role="alert">
          Error al guardar la configuración. Intente nuevamente.
        </p>
      )}

      <div className="flex justify-end gap-3 pt-2">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
        )}
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending
            ? 'Guardando...'
            : isEditing
              ? 'Actualizar'
              : 'Crear'}
        </Button>
      </div>
    </form>
  );
}
