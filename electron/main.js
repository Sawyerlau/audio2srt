"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
let mainWindow = null;
const isDev = process.env.NODE_ENV === 'development' || !electron_1.app.isPackaged;
function createWindow() {
    mainWindow = new electron_1.BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 900,
        minHeight: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        },
        icon: path.join(__dirname, '../image/ico.png')
    });
    // 隐藏顶部菜单栏
    electron_1.Menu.setApplicationMenu(null);
    if (isDev) {
        mainWindow.loadURL('http://localhost:5173').catch(() => {
            mainWindow?.loadURL('http://localhost:5174');
        });
    }
    else {
        mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    }
    mainWindow.webContents.on('will-navigate', (e) => {
        e.preventDefault();
    });
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}
electron_1.app.whenReady().then(() => {
    createWindow();
});
electron_1.app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        electron_1.app.quit();
    }
});
electron_1.app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});
const CONFIG_FILE = 'audio2srt_config.json';
const DEFAULT_CONFIG = {
    API_KEY: '',
    RESOURCE_ID: 'volc.bigasr.auc'
};
function getConfigPath() {
    return path.join(electron_1.app.getPath('userData'), CONFIG_FILE);
}
function loadConfig() {
    const configPath = getConfigPath();
    if (fs.existsSync(configPath)) {
        try {
            const data = fs.readFileSync(configPath, 'utf-8');
            return { ...DEFAULT_CONFIG, ...JSON.parse(data) };
        }
        catch {
            return { ...DEFAULT_CONFIG };
        }
    }
    return { ...DEFAULT_CONFIG };
}
function saveConfig(config) {
    const configPath = getConfigPath();
    const configDir = path.dirname(configPath);
    if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
    }
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8');
}
electron_1.ipcMain.handle('config:load', () => loadConfig());
electron_1.ipcMain.handle('config:save', (_event, config) => {
    saveConfig(config);
    return true;
});
electron_1.ipcMain.handle('dialog:openFiles', async () => {
    const result = await electron_1.dialog.showOpenDialog(mainWindow, {
        properties: ['openFile', 'multiSelections'],
        filters: [
            { name: '音频和视频文件', extensions: ['mp3', 'wav', 'm4a', 'flac', 'aac', 'ogg', 'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm', 'm4v'] },
            { name: '所有文件', extensions: ['*'] }
        ]
    });
    return result.filePaths;
});
electron_1.ipcMain.handle('dialog:openFile', async () => {
    const result = await electron_1.dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [
            { name: 'SRT文件', extensions: ['srt'] },
            { name: '所有文件', extensions: ['*'] }
        ]
    });
    return result.filePaths[0];
});
electron_1.ipcMain.handle('python:processAudio', async (_event, options) => {
    return new Promise((resolve, reject) => {
        const { spawn } = require('child_process');
        const pythonScript = path.join(__dirname, '../python_backend/electron_bridge.py');
        const args = [
            'process_audio',
            JSON.stringify(options)
        ];
        const python = spawn('python', [pythonScript, ...args]);
        let output = '';
        let error = '';
        python.stdout?.on('data', (data) => {
            const log = data.toString();
            output += log;
            const lines = log.split('\n');
            for (const line of lines) {
                const trimmed = line.trim();
                if (trimmed) {
                    console.log(trimmed);
                    if (mainWindow) {
                        mainWindow.webContents.send('python:log', trimmed);
                    }
                }
            }
        });
        python.stderr?.on('data', (data) => {
            const log = data.toString();
            error += log;
            const lines = log.split('\n');
            for (const line of lines) {
                const trimmed = line.trim();
                if (trimmed) {
                    console.error(trimmed);
                    if (mainWindow) {
                        mainWindow.webContents.send('python:log', trimmed);
                    }
                }
            }
        });
        python.on('close', (code) => {
            if (code === 0) {
                try {
                    resolve(JSON.parse(output));
                }
                catch {
                    resolve({ success: true, output });
                }
            }
            else {
                reject(new Error(error || 'Python script failed'));
            }
        });
    });
});
electron_1.ipcMain.handle('python:optimizeSrt', async (_event, options) => {
    return new Promise((resolve, reject) => {
        const { spawn } = require('child_process');
        const pythonScript = path.join(__dirname, '../python_backend/electron_bridge.py');
        const args = [
            'optimize_srt',
            JSON.stringify(options)
        ];
        const python = spawn('python', [pythonScript, ...args]);
        let output = '';
        let error = '';
        python.stdout?.on('data', (data) => {
            const log = data.toString();
            output += log;
            const lines = log.split('\n');
            for (const line of lines) {
                const trimmed = line.trim();
                if (trimmed) {
                    console.log(trimmed);
                    if (mainWindow) {
                        mainWindow.webContents.send('python:log', trimmed);
                    }
                }
            }
        });
        python.stderr?.on('data', (data) => {
            const log = data.toString();
            error += log;
            const lines = log.split('\n');
            for (const line of lines) {
                const trimmed = line.trim();
                if (trimmed) {
                    console.error(trimmed);
                    if (mainWindow) {
                        mainWindow.webContents.send('python:log', trimmed);
                    }
                }
            }
        });
        python.on('close', (code) => {
            if (code === 0) {
                try {
                    resolve(JSON.parse(output));
                }
                catch {
                    resolve({ success: true, output });
                }
            }
            else {
                reject(new Error(error || 'Python script failed'));
            }
        });
    });
});
