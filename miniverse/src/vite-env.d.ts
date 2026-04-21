/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_MINIVERSE_API?: string;
  readonly VITE_MINIVERSE_WS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
