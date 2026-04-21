/**
 * Tests unitarios: audit-data (ZONES, createEmptyReport, categorizeMessage)
 */
import { describe, it, expect } from "vitest";
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const {
  ZONES,
  createEmptyReport,
  categorizeMessage,
} = require("../../scripts/audit-data.js");

describe("ZONES (audit)", () => {
  it("tiene al menos una zona por defecto", () => {
    expect(ZONES.length).toBeGreaterThanOrEqual(1);
  });

  it("cada zona tiene name y url", () => {
    ZONES.forEach((zone) => {
      expect(zone).toHaveProperty("name");
      expect(zone).toHaveProperty("url");
      expect(typeof zone.name).toBe("string");
      expect(typeof zone.url).toBe("string");
    });
  });

  it("incluye Home como zona por defecto", () => {
    const names = ZONES.map((z) => z.name);
    expect(names).toContain("Home");
  });

  it("urls comienzan con /", () => {
    ZONES.forEach((zone) => {
      expect(zone.url.startsWith("/")).toBe(true);
    });
  });
});

describe("createEmptyReport", () => {
  it("devuelve estructura con timestamp, zones, allConsoleMessages, summary", () => {
    const report = createEmptyReport();
    expect(report).toHaveProperty("timestamp");
    expect(report).toHaveProperty("zones");
    expect(report).toHaveProperty("allConsoleMessages");
    expect(report).toHaveProperty("summary");
    expect(Array.isArray(report.zones)).toBe(true);
    expect(Array.isArray(report.allConsoleMessages)).toBe(true);
    expect(report.summary).toEqual({ errors: 0, warnings: 0, logs: 0 });
  });

  it("timestamp es ISO8601", () => {
    const report = createEmptyReport();
    expect(new Date(report.timestamp).toISOString()).toBe(report.timestamp);
  });
});

describe("categorizeMessage", () => {
  it("incrementa errors para type error", () => {
    const summary = { errors: 0, warnings: 0, logs: 0 };
    categorizeMessage("error", summary);
    categorizeMessage("error", summary);
    expect(summary.errors).toBe(2);
    expect(summary.warnings).toBe(0);
    expect(summary.logs).toBe(0);
  });

  it("incrementa warnings para type warning", () => {
    const summary = { errors: 0, warnings: 0, logs: 0 };
    categorizeMessage("warning", summary);
    expect(summary.warnings).toBe(1);
  });

  it("incrementa logs para otros tipos", () => {
    const summary = { errors: 0, warnings: 0, logs: 0 };
    categorizeMessage("log", summary);
    categorizeMessage("info", summary);
    expect(summary.logs).toBe(2);
  });
});
