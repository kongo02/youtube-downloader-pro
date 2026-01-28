const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
    'electronAPI', {
        // Download management
        startDownload: (url, filename) => 
            ipcRenderer.invoke('download:start', { url, filename }),
        
        getDownloadProgress: (callback) => 
            ipcRenderer.on('download:progress', callback),
        
        getDownloadComplete: (callback) => 
            ipcRenderer.on('download:complete', callback),
        
        getDownloadError: (callback) => 
            ipcRenderer.on('download:error', callback),
        
        // Backend management
        checkBackend: () => 
            ipcRenderer.invoke('backend:check'),
        
        startBackend: () => 
            ipcRenderer.invoke('backend:start'),
        
        stopBackend: () => 
            ipcRenderer.invoke('backend:stop'),
        
        // File system (limited)
        openDownloadFolder: () => 
            ipcRenderer.invoke('folder:open'),
        
        getDownloadsList: () => 
            ipcRenderer.invoke('folder:list'),
        
        // Window controls
        minimizeWindow: () => 
            ipcRenderer.send('window:minimize'),
        
        maximizeWindow: () => 
            ipcRenderer.send('window:maximize'),
        
        closeWindow: () => 
            ipcRenderer.send('window:close'),
        
        // App info
        getAppVersion: () => 
            ipcRenderer.invoke('app:version')
    }
);

// Add a safe console wrapper for renderer
contextBridge.exposeInMainWorld('console', {
    log: (...args) => ipcRenderer.send('console:log', ...args),
    error: (...args) => ipcRenderer.send('console:error', ...args),
    warn: (...args) => ipcRenderer.send('console:warn', ...args)
});