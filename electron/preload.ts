import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  config: {
    load: () => ipcRenderer.invoke('config:load'),
    save: (config: any) => ipcRenderer.invoke('config:save', config)
  },
  dialog: {
    openFiles: () => ipcRenderer.invoke('dialog:openFiles'),
    openFile: () => ipcRenderer.invoke('dialog:openFile')
  },
  python: {
    processAudio: (options: any) => ipcRenderer.invoke('python:processAudio', options),
    optimizeSrt: (options: any) => ipcRenderer.invoke('python:optimizeSrt', options),
    onLog: (callback: (log: string) => void) => {
      ipcRenderer.on('python:log', (_event, log) => callback(log));
    }
  }
});
