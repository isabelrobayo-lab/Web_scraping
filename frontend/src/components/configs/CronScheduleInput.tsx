/**
 * CronScheduleInput — Cron expression input with human-readable preview.
 *
 * Shows a text input for the cron expression and a preview of the
 * schedule in human-readable Spanish. (Req 1.4)
 */

import { useMemo } from 'react';

interface CronScheduleInputProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
}

const CRON_PATTERN = /^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$/;

/** Simple cron-to-Spanish preview. */
function cronToHuman(cron: string): string | null {
  const match = cron.trim().match(CRON_PATTERN);
  if (!match) return null;

  const [, minute, hour, dayOfMonth, month, dayOfWeek] = match;

  const dayNames: Record<string, string> = {
    '0': 'domingo', '1': 'lunes', '2': 'martes', '3': 'miércoles',
    '4': 'jueves', '5': 'viernes', '6': 'sábado', '7': 'domingo',
  };

  const parts: string[] = [];

  if (minute !== '*' && hour !== '*') {
    parts.push(`a las ${hour.padStart(2, '0')}:${minute.padStart(2, '0')}`);
  } else if (hour !== '*') {
    parts.push(`cada minuto de la hora ${hour}`);
  } else if (minute !== '*') {
    parts.push(`en el minuto ${minute} de cada hora`);
  } else {
    parts.push('cada minuto');
  }

  if (dayOfWeek !== '*') {
    const days = dayOfWeek.split(',').map((d) => dayNames[d] ?? d).join(', ');
    parts.push(`los ${days}`);
  }

  if (dayOfMonth !== '*') {
    parts.push(`el día ${dayOfMonth} del mes`);
  }

  if (month !== '*') {
    parts.push(`en el mes ${month}`);
  }

  return parts.join(', ');
}

export function CronScheduleInput({ value, onChange, error }: CronScheduleInputProps) {
  const preview = useMemo(() => cronToHuman(value || ''), [value]);

  return (
    <div className="space-y-2">
      <label htmlFor="cron_expression" className="text-sm font-medium">
        Expresión Cron
      </label>
      <input
        id="cron_expression"
        type="text"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder="0 8 * * 1-5"
        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        aria-describedby="cron-preview"
      />
      {preview && (
        <p id="cron-preview" className="text-xs text-muted-foreground">
          Programación: {preview}
        </p>
      )}
      {error && (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
