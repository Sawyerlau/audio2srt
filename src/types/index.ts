export interface Config {
  API_KEY: string;
  RESOURCE_ID: string;
}

export interface FileItem {
  id: string;
  path: string;
  name: string;
  type: 'audio' | 'video';
}

export interface HelpSection {
  title: string;
  content: string;
  expanded?: boolean;
}

export interface PythonProcessResult {
  success: boolean;
}

export interface PythonAPI {
  onLog: (callback: (log: string) => void) => (() => void);
  processAudio: (params: { type: string; inputs: string[]; config: Config }) => Promise<PythonProcessResult>;
}

export interface DialogAPI {
  openFiles: () => Promise<string[]>;
}

export interface ConfigAPI {
  load: () => Promise<Partial<Config>>;
  save: (config: Config) => Promise<void>;
}

export interface ElectronAPI {
  python?: PythonAPI;
  dialog?: DialogAPI;
  config?: ConfigAPI;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}
