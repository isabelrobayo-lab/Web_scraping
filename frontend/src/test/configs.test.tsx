/**
 * Vitest unit tests for config form validation schemas and component rendering.
 *
 * Tests Task 17.6: Zod schema validation and basic component rendering.
 */

import { describe, it, expect } from 'vitest';

import { configCreateSchema } from '@/schemas/config';
import { render, screen } from '@/test/test-utils';
import { CronScheduleInput } from '@/components/configs/CronScheduleInput';
import { ConfirmDialog } from '@/components/shared/ConfirmDialog';
import { Pagination } from '@/components/shared/Pagination';

// ---------------------------------------------------------------------------
// Zod Schema Validation Tests
// ---------------------------------------------------------------------------

describe('configCreateSchema', () => {
  it('accepts a valid manual configuration', () => {
    const result = configCreateSchema.safeParse({
      url_base: 'https://www.ejemplo.com/inmuebles',
      profundidad_navegacion: 3,
      tipo_operacion: 'Venta',
      modo_ejecucion: 'Manual',
      cron_expression: null,
    });
    expect(result.success).toBe(true);
  });

  it('accepts a valid programmed configuration with cron', () => {
    const result = configCreateSchema.safeParse({
      url_base: 'https://www.ejemplo.com',
      profundidad_navegacion: 5,
      tipo_operacion: 'Arriendo',
      modo_ejecucion: 'Programado',
      cron_expression: '0 8 * * 1-5',
    });
    expect(result.success).toBe(true);
  });

  it('rejects an invalid URL', () => {
    const result = configCreateSchema.safeParse({
      url_base: 'not-a-url',
      profundidad_navegacion: 3,
      tipo_operacion: 'Venta',
      modo_ejecucion: 'Manual',
    });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues.some((i) => i.path.includes('url_base'))).toBe(true);
    }
  });

  it('rejects depth below 1', () => {
    const result = configCreateSchema.safeParse({
      url_base: 'https://www.ejemplo.com',
      profundidad_navegacion: 0,
      tipo_operacion: 'Venta',
      modo_ejecucion: 'Manual',
    });
    expect(result.success).toBe(false);
  });

  it('rejects depth above 10', () => {
    const result = configCreateSchema.safeParse({
      url_base: 'https://www.ejemplo.com',
      profundidad_navegacion: 11,
      tipo_operacion: 'Venta',
      modo_ejecucion: 'Manual',
    });
    expect(result.success).toBe(false);
  });

  it('requires cron when modo_ejecucion is Programado', () => {
    const result = configCreateSchema.safeParse({
      url_base: 'https://www.ejemplo.com',
      profundidad_navegacion: 3,
      tipo_operacion: 'Venta',
      modo_ejecucion: 'Programado',
      cron_expression: null,
    });
    expect(result.success).toBe(false);
  });

  it('rejects invalid cron expression for Programado', () => {
    const result = configCreateSchema.safeParse({
      url_base: 'https://www.ejemplo.com',
      profundidad_navegacion: 3,
      tipo_operacion: 'Venta',
      modo_ejecucion: 'Programado',
      cron_expression: 'invalid',
    });
    expect(result.success).toBe(false);
  });

  it('rejects empty URL', () => {
    const result = configCreateSchema.safeParse({
      url_base: '',
      profundidad_navegacion: 3,
      tipo_operacion: 'Venta',
      modo_ejecucion: 'Manual',
    });
    expect(result.success).toBe(false);
  });

  it('accepts depth boundary values 1 and 10', () => {
    const result1 = configCreateSchema.safeParse({
      url_base: 'https://www.ejemplo.com',
      profundidad_navegacion: 1,
      tipo_operacion: 'Venta',
      modo_ejecucion: 'Manual',
    });
    const result10 = configCreateSchema.safeParse({
      url_base: 'https://www.ejemplo.com',
      profundidad_navegacion: 10,
      tipo_operacion: 'Arriendo',
      modo_ejecucion: 'Manual',
    });
    expect(result1.success).toBe(true);
    expect(result10.success).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Component Rendering Tests
// ---------------------------------------------------------------------------

describe('CronScheduleInput', () => {
  it('renders input and label', () => {
    render(
      <CronScheduleInput value="" onChange={() => {}} />,
    );
    expect(screen.getByLabelText('Expresión Cron')).toBeInTheDocument();
  });

  it('shows human-readable preview for valid cron', () => {
    render(
      <CronScheduleInput value="0 8 * * 1" onChange={() => {}} />,
    );
    expect(screen.getByText(/Programación:/)).toBeInTheDocument();
  });

  it('shows error message when provided', () => {
    render(
      <CronScheduleInput value="" onChange={() => {}} error="Campo requerido" />,
    );
    expect(screen.getByText('Campo requerido')).toBeInTheDocument();
  });
});

describe('ConfirmDialog', () => {
  it('renders when open', () => {
    render(
      <ConfirmDialog
        open={true}
        title="Confirmar acción"
        description="¿Está seguro?"
        onConfirm={() => {}}
        onCancel={() => {}}
      />,
    );
    expect(screen.getByText('Confirmar acción')).toBeInTheDocument();
    expect(screen.getByText('¿Está seguro?')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <ConfirmDialog
        open={false}
        title="Confirmar acción"
        description="¿Está seguro?"
        onConfirm={() => {}}
        onCancel={() => {}}
      />,
    );
    expect(screen.queryByText('Confirmar acción')).not.toBeInTheDocument();
  });
});

describe('Pagination', () => {
  it('renders page info', () => {
    render(
      <Pagination page={2} pages={5} total={50} onPageChange={() => {}} />,
    );
    expect(screen.getByText(/Página 2 de 5/)).toBeInTheDocument();
  });

  it('does not render when only one page', () => {
    const { container } = render(
      <Pagination page={1} pages={1} total={5} onPageChange={() => {}} />,
    );
    expect(container.innerHTML).toBe('');
  });
});
