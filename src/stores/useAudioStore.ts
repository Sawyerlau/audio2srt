import { create } from 'zustand';
import { FileItem } from '../types';

interface AudioState {
  mode: 'local' | 'url';
  files: FileItem[];
  urls: string;
  logs: string[];
  progress: number;
  isProcessing: boolean;
  setMode: (mode: 'local' | 'url') => void;
  addFiles: (paths: string[]) => void;
  removeFile: (id: string) => void;
  clearFiles: () => void;
  setUrls: (urls: string) => void;
  addLog: (log: string) => void;
  clearLogs: () => void;
  setProgress: (progress: number) => void;
  setIsProcessing: (processing: boolean) => void;
}

function getFileType(path: string): 'audio' | 'video' {
  const ext = path.split('.').pop()?.toLowerCase();
  const videoExts = new Set(['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm', 'm4v']);
  return videoExts.has(ext || '') ? 'video' : 'audio';
}

export const useAudioStore = create<AudioState>((set) => {
  let lastLog = '';

  return {
    mode: 'local',
    files: [],
    urls: '',
    logs: [],
    progress: 0,
    isProcessing: false,

    setMode: (mode) => set({ mode }),

    addFiles: (paths) => set((state) => {
      const newFiles = paths.map((path) => {
        return {
          id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
          path,
          name: path.split(/[/\\]/).pop() || '',
          type: getFileType(path)
        };
      });
      return { files: [...state.files, ...newFiles] };
    }),

    removeFile: (id) => set((state) => ({
      files: state.files.filter((f) => f.id !== id)
    })),

    clearFiles: () => set({ files: [] }),

    setUrls: (urls) => set({ urls }),

    addLog: (log) => set((state) => {
      if (log === lastLog) return state;
      lastLog = log;
      return { logs: [...state.logs, log] };
    }),

    clearLogs: () => set((state) => {
      lastLog = '';
      return { logs: [] };
    }),

    setProgress: (progress) => set({ progress }),

    setIsProcessing: (processing) => set({ isProcessing: processing })
  };
});
