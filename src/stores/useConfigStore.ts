import { create } from 'zustand';
import { Config } from '../types';

interface ConfigStore {
  config: Config;
  setConfig: (config: Config) => void;
  loadConfig: () => Promise<void>;
  saveConfig: () => Promise<void>;
}

const DEFAULT_CONFIG: Config = {
  API_KEY: '',
  RESOURCE_ID: 'volc.bigasr.auc'
};

export const useConfigStore = create<ConfigStore>((set, get) => ({
  config: DEFAULT_CONFIG,

  setConfig: (config) => set({ config }),

  loadConfig: async () => {
    try {
      if (!window.electronAPI?.config?.load) return;
      const loaded = await window.electronAPI.config.load();
      set({ config: { ...DEFAULT_CONFIG, ...loaded } });
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  },

  saveConfig: async () => {
    try {
      if (!window.electronAPI?.config?.save) return;
      await window.electronAPI.config.save(get().config);
    } catch (error) {
      console.error('Failed to save config:', error);
    }
  }
}));
