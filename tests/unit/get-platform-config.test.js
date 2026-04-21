/**
 * Tests unitarios: get-platform-config (getPlatformConfig, getBaseUrl, getSmokePaths, getAuditZones, getAllPlatforms)
 * Usa PLATFORMS_CONFIG_PATH para apuntar a archivos de prueba en un directorio temporal.
 */
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { createRequire } from "module";
import fs from "fs";
import path from "path";
import os from "os";

const require = createRequire(import.meta.url);
const {
  getPlatformConfig,
  getBaseUrl,
  getSmokePaths,
  getAuditZones,
  getAllPlatforms,
  getPlatformsConfig,
} = require("../../scripts/get-platform-config.js");

let tempDir;
let originalConfigPath;
let originalBaseUrl;
let originalPlatformId;

const mockPlatform = {
  id: "ejemplo",
  name: "Ejemplo",
  urls: { app: "https://www.ejemplo.com", staging: "https://staging.ejemplo.com" },
  smokePaths: ["/", "/ruta1", "/ruta2"],
  auditZones: [
    { name: "Home", url: "/" },
    { name: "Sección A", url: "/ruta1" },
  ],
};

const mockConfig = {
  platforms: [mockPlatform],
  defaultPlatformId: "ejemplo",
};

describe("get-platform-config", () => {
  beforeEach(() => {
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "platform-config-test-"));
    originalConfigPath = process.env.PLATFORMS_CONFIG_PATH;
    originalBaseUrl = process.env.BASE_URL;
    originalPlatformId = process.env.PLATFORM_ID;
  });

  afterEach(() => {
    if (tempDir && fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
    process.env.PLATFORMS_CONFIG_PATH = originalConfigPath;
    process.env.BASE_URL = originalBaseUrl;
    if (originalPlatformId === undefined) {
      delete process.env.PLATFORM_ID;
    } else {
      process.env.PLATFORM_ID = originalPlatformId;
    }
  });

  describe("getPlatformsConfig", () => {
    it("devuelve null cuando no existe platforms.json", () => {
      process.env.PLATFORMS_CONFIG_PATH = path.join(tempDir, "no-existe.json");
      expect(getPlatformsConfig()).toBeNull();
    });

    it("devuelve config parseada cuando existe el archivo", () => {
      const configPath = path.join(tempDir, "platforms.json");
      fs.writeFileSync(configPath, JSON.stringify(mockConfig), "utf-8");
      process.env.PLATFORMS_CONFIG_PATH = configPath;
      expect(getPlatformsConfig()).toEqual(mockConfig);
    });
  });

  describe("getPlatformConfig", () => {
    it("devuelve null cuando no hay config", () => {
      process.env.PLATFORMS_CONFIG_PATH = path.join(tempDir, "no-existe.json");
      expect(getPlatformConfig()).toBeNull();
    });

    it("devuelve la plataforma por defaultPlatformId cuando coincide", () => {
      const configPath = path.join(tempDir, "platforms.json");
      fs.writeFileSync(configPath, JSON.stringify(mockConfig), "utf-8");
      process.env.PLATFORMS_CONFIG_PATH = configPath;
      expect(getPlatformConfig()).toEqual(mockPlatform);
    });

    it("devuelve la primera plataforma cuando defaultPlatformId no coincide", () => {
      const configNoMatch = {
        platforms: [mockPlatform],
        defaultPlatformId: "otra-id",
      };
      const configPath = path.join(tempDir, "platforms.json");
      fs.writeFileSync(configPath, JSON.stringify(configNoMatch), "utf-8");
      process.env.PLATFORMS_CONFIG_PATH = configPath;
      expect(getPlatformConfig()).toEqual(mockPlatform);
    });

    it("usa PLATFORM_ID cuando coincide con una plataforma", () => {
      const platformB = { ...mockPlatform, id: "b", name: "B" };
      const configPath = path.join(tempDir, "platforms.json");
      fs.writeFileSync(
        configPath,
        JSON.stringify({
          platforms: [mockPlatform, platformB],
          defaultPlatformId: "ejemplo",
        }),
        "utf-8",
      );
      process.env.PLATFORMS_CONFIG_PATH = configPath;
      process.env.PLATFORM_ID = "b";
      expect(getPlatformConfig()).toEqual(platformB);
    });

    it("ignora PLATFORM_ID si no existe en la lista y usa defaultPlatformId", () => {
      const configPath = path.join(tempDir, "platforms.json");
      fs.writeFileSync(configPath, JSON.stringify(mockConfig), "utf-8");
      process.env.PLATFORMS_CONFIG_PATH = configPath;
      process.env.PLATFORM_ID = "inexistente";
      expect(getPlatformConfig()).toEqual(mockPlatform);
    });
  });

  describe("getBaseUrl", () => {
    it("devuelve platform.urls.app cuando hay config", () => {
      const configPath = path.join(tempDir, "platforms.json");
      fs.writeFileSync(configPath, JSON.stringify(mockConfig), "utf-8");
      process.env.PLATFORMS_CONFIG_PATH = configPath;
      expect(getBaseUrl()).toBe("https://www.ejemplo.com");
    });

    it("devuelve null cuando no hay config y no hay BASE_URL en env", () => {
      process.env.PLATFORMS_CONFIG_PATH = path.join(tempDir, "no-existe.json");
      delete process.env.BASE_URL;
      expect(getBaseUrl()).toBeNull();
    });

    it("devuelve process.env.BASE_URL cuando no hay platform", () => {
      process.env.PLATFORMS_CONFIG_PATH = path.join(tempDir, "no-existe.json");
      process.env.BASE_URL = "https://fallback.com";
      expect(getBaseUrl()).toBe("https://fallback.com");
    });
  });

  describe("getSmokePaths", () => {
    it("devuelve smokePaths de la plataforma cuando existen", () => {
      const configPath = path.join(tempDir, "platforms.json");
      fs.writeFileSync(configPath, JSON.stringify(mockConfig), "utf-8");
      process.env.PLATFORMS_CONFIG_PATH = configPath;
      expect(getSmokePaths()).toEqual(["/", "/ruta1", "/ruta2"]);
    });

    it("devuelve ['/'] por defecto cuando no hay config", () => {
      process.env.PLATFORMS_CONFIG_PATH = path.join(tempDir, "no-existe.json");
      expect(getSmokePaths()).toEqual(["/"]);
    });

    it("devuelve ['/'] cuando platform no tiene smokePaths", () => {
      const configSinSmoke = {
        platforms: [{ ...mockPlatform, smokePaths: undefined }],
        defaultPlatformId: "ejemplo",
      };
      const configPath = path.join(tempDir, "platforms.json");
      fs.writeFileSync(configPath, JSON.stringify(configSinSmoke), "utf-8");
      process.env.PLATFORMS_CONFIG_PATH = configPath;
      expect(getSmokePaths()).toEqual(["/"]);
    });
  });

  describe("getAuditZones", () => {
    it("devuelve auditZones de la plataforma cuando existen", () => {
      const configPath = path.join(tempDir, "platforms.json");
      fs.writeFileSync(configPath, JSON.stringify(mockConfig), "utf-8");
      process.env.PLATFORMS_CONFIG_PATH = configPath;
      expect(getAuditZones()).toEqual([
        { name: "Home", url: "/" },
        { name: "Sección A", url: "/ruta1" },
      ]);
    });

    it("devuelve Home por defecto cuando no hay config", () => {
      process.env.PLATFORMS_CONFIG_PATH = path.join(tempDir, "no-existe.json");
      expect(getAuditZones()).toEqual([{ name: "Home", url: "/" }]);
    });

    it("devuelve Home por defecto cuando auditZones está vacío", () => {
      const configSinZones = {
        platforms: [{ ...mockPlatform, auditZones: [] }],
        defaultPlatformId: "ejemplo",
      };
      const configPath = path.join(tempDir, "platforms.json");
      fs.writeFileSync(configPath, JSON.stringify(configSinZones), "utf-8");
      process.env.PLATFORMS_CONFIG_PATH = configPath;
      expect(getAuditZones()).toEqual([{ name: "Home", url: "/" }]);
    });
  });

  describe("getAllPlatforms", () => {
    it("devuelve array de plataformas cuando hay config", () => {
      const configPath = path.join(tempDir, "platforms.json");
      fs.writeFileSync(configPath, JSON.stringify(mockConfig), "utf-8");
      process.env.PLATFORMS_CONFIG_PATH = configPath;
      expect(getAllPlatforms()).toEqual([mockPlatform]);
    });

    it("devuelve array vacío cuando no hay config", () => {
      process.env.PLATFORMS_CONFIG_PATH = path.join(tempDir, "no-existe.json");
      expect(getAllPlatforms()).toEqual([]);
    });
  });
});
