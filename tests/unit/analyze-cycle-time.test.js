/**
 * Tests unitarios: analyze-cycle-time (formatHours, analyzeFromData, report)
 */
import { describe, it, expect } from "vitest";
import { createRequire } from "module";

const require = createRequire(import.meta.url);
const { analyzeFromData, formatHours, report } = require("../../tools/scripts/analyze-cycle-time.js");

describe("formatHours", () => {
  it("devuelve '—' para null o NaN", () => {
    expect(formatHours(null)).toBe("—");
    expect(formatHours(undefined)).toBe("—");
    expect(formatHours(NaN)).toBe("—");
  });

  it("devuelve '0h' para cero", () => {
    expect(formatHours(0)).toBe("0h");
  });

  it("formatea horas menores a 24", () => {
    expect(formatHours(1)).toBe("1h");
    expect(formatHours(5.5)).toBe("5.5h");
    expect(formatHours(23.456)).toBe("23.5h");
  });

  it("formatea días cuando >= 24 horas", () => {
    expect(formatHours(24)).toBe("1d");
    expect(formatHours(48)).toBe("2d");
    expect(formatHours(36)).toBe("1d 12.0h");
    expect(formatHours(25)).toBe("1d 1.0h");
  });

  it("redondea correctamente", () => {
    expect(formatHours(1.04)).toBe("1h");
    expect(formatHours(1.05)).toBe("1.1h");
  });
});

describe("analyzeFromData", () => {
  it("lanza error con formato inválido (sin issues)", () => {
    expect(() => analyzeFromData({ foo: "bar" })).toThrow(
      "Formato inválido: se esperaba { issues: [...] }"
    );
  });

  it("lanza error cuando issues no es array", () => {
    expect(() => analyzeFromData({ issues: "not-array" })).toThrow(
      "Formato inválido: se esperaba { issues: [...] }"
    );
  });

  it("devuelve stats, byProject y totalIssues con issues vacío", () => {
    const result = analyzeFromData({ issues: [] });
    expect(result).toHaveProperty("stats");
    expect(result).toHaveProperty("byProject");
    expect(result.totalIssues).toBe(0);
    expect(Object.keys(result.stats).length).toBeGreaterThan(0);
  });

  it("acumula valores de tiempo por field y por proyecto", () => {
    const issues = [
      {
        fields: {
          project: { key: "PROJ1" },
          customfield_24748: 10,
          customfield_24759: 2,
        },
      },
      {
        fields: {
          project: { key: "PROJ1" },
          customfield_24748: 20,
          customfield_24764: 5,
        },
      },
    ];
    const result = analyzeFromData({ issues });
    expect(result.totalIssues).toBe(2);
    expect(result.stats.customfield_24748.values).toEqual([10, 20]);
    expect(result.stats.customfield_24748.sum).toBe(30);
    expect(result.stats.customfield_24748.count).toBe(2);
    expect(result.byProject.PROJ1).toBeDefined();
    expect(result.byProject.PROJ1.customfield_24748.values).toEqual([10, 20]);
  });

  it("usa N/A cuando issue no tiene project", () => {
    const issues = [{ fields: { customfield_24748: 5 } }];
    const result = analyzeFromData({ issues });
    expect(result.byProject["N/A"]).toBeDefined();
  });

  it("ignora valores NaN, negativos o no numéricos", () => {
    const issues = [
      {
        fields: {
          project: { key: "P" },
          customfield_24748: -1,
          customfield_24759: NaN,
          customfield_24764: "text",
          customfield_24765: null,
        },
      },
    ];
    const result = analyzeFromData({ issues });
    expect(result.stats.customfield_24748.count).toBe(0);
    expect(result.stats.customfield_24759.count).toBe(0);
  });
});

describe("report", () => {
  it("genera markdown con estructura esperada", () => {
    const emptyField = { values: [], sum: 0, count: 0 };
    const fakeResult = {
      stats: {
        customfield_24748: { values: [24], sum: 24, count: 1 },
        customfield_24759: { values: [2], sum: 2, count: 1 },
        customfield_24764: emptyField,
        customfield_24765: emptyField,
        customfield_24767: emptyField,
        customfield_24757: emptyField,
        customfield_24762: emptyField,
      },
      byProject: {
        PROJ: {
          customfield_24748: { values: [24], sum: 24, count: 1 },
          customfield_24759: emptyField,
          customfield_24764: emptyField,
          customfield_24765: emptyField,
          customfield_24767: emptyField,
          customfield_24757: emptyField,
          customfield_24762: emptyField,
        },
      },
      totalIssues: 1,
    };
    const md = report(fakeResult);
    expect(md).toContain("# Análisis de tiempo por fase del ciclo de desarrollo");
    expect(md).toContain("**Muestra:** 1 Historias de Usuario cerradas");
    expect(md).toContain("Promedio de horas por fase");
    expect(md).toContain("Por proyecto");
  });
});
