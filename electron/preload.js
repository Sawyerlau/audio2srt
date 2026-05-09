"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
electron_1.contextBridge.exposeInMainWorld('electronAPI', {
    config: {
        load: () => electron_1.ipcRenderer.invoke('config:load'),
        save: (config) => electron_1.ipcRenderer.invoke('config:save', config)
    },
    dialog: {
        openFiles: () => electron_1.ipcRenderer.invoke('dialog:openFiles'),
        openFile: () => electron_1.ipcRenderer.invoke('dialog:openFile')
    },
    python: {
        processAudio: (options) => electron_1.ipcRenderer.invoke('python:processAudio', options),
        optimizeSrt: (options) => electron_1.ipcRenderer.invoke('python:optimizeSrt', options),
        onLog: (callback) => {
            electron_1.ipcRenderer.on('python:log', (_event, log) => callback(log));
        }
    }
});
