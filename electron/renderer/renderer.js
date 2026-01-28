// Main renderer process JavaScript
class YouTubeDownloaderApp {
    constructor() {
        this.currentDownloads = new Map();
        this.init();
    }

    async init() {
        // Check backend status on load
        await this.checkBackendStatus();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup WebSocket listeners
        this.setupWebSocketListeners();
        
        // Load existing downloads
        await this.loadExistingDownloads();
        
        console.log('YouTube Downloader Pro initialized');
    }

    async checkBackendStatus() {
        const isRunning = await window.electronAPI.checkBackend();
        this.updateBackendStatus(isRunning);
        
        if (!isRunning) {
            // Try to start backend
            const started = await window.electronAPI.startBackend();
            if (started) {
                setTimeout(() => this.checkBackendStatus(), 2000);
            }
        }
    }

    updateBackendStatus(isRunning) {
        const statusElement = document.getElementById('backendStatus');
        if (statusElement) {
            statusElement.textContent = isRunning ? '✓ Backend Running' : '✗ Backend Stopped';
            statusElement.className = `status-${isRunning ? 'running' : 'stopped'}`;
        }
    }

    setupEventListeners() {
        // Download form
        document.getElementById('downloadBtn').addEventListener('click', () => this.startDownload());
        
        // Enter key support
        document.getElementById('url').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.startDownload();
        });
        
        document.getElementById('filename').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.startDownload();
        });
        
        // Open download folder
        document.getElementById('openFolderBtn')?.addEventListener('click', () => {
            window.electronAPI.openDownloadFolder();
        });
        
        // Window controls
        document.getElementById('minimizeBtn')?.addEventListener('click', () => {
            window.electronAPI.minimizeWindow();
        });
        
        document.getElementById('maximizeBtn')?.addEventListener('click', () => {
            window.electronAPI.maximizeWindow();
        });
        
        document.getElementById('closeBtn')?.addEventListener('click', () => {
            window.electronAPI.closeWindow();
        });
    }

    setupWebSocketListeners() {
        // Progress updates
        window.electronAPI.getDownloadProgress((event, data) => {
            this.updateDownloadProgress(data);
        });
        
        // Completion
        window.electronAPI.getDownloadComplete((event, data) => {
            this.handleDownloadComplete(data);
        });
        
        // Errors
        window.electronAPI.getDownloadError((event, data) => {
            this.handleDownloadError(data);
        });
    }

    async startDownload() {
        const url = document.getElementById('url').value.trim();
        const filename = document.getElementById('filename').value.trim();
        
        if (!this.validateInputs(url, filename)) {
            return;
        }
        
        // Update UI
        this.showLoadingState();
        
        try {
            const result = await window.electronAPI.startDownload(url, filename);
            
            if (result.success) {
                this.showSuccess('Download started successfully!');
                this.clearForm();
                this.addToDownloadsList(filename, url);
            } else {
                this.showError(`Failed to start download: ${result.error}`);
            }
        } catch (error) {
            this.showError(`Error: ${error.message}`);
        } finally {
            this.hideLoadingState();
        }
    }

    validateInputs(url, filename) {
        if (!url) {
            this.showError('Please enter a YouTube URL');
            return false;
        }
        
        if (!filename) {
            this.showError('Please enter a filename');
            return false;
        }
        
        // Basic URL validation
        if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
            if (!confirm("This doesn't look like a YouTube URL. Continue anyway?")) {
                return false;
            }
        }
        
        return true;
    }

    updateDownloadProgress(data) {
        const { filename, percent, speed, eta } = data;
        
        // Update progress bar
        const progressBar = document.getElementById('progressBar');
        const percentText = document.getElementById('progressPercent');
        const speedText = document.getElementById('progressSpeed');
        const etaText = document.getElementById('progressETA');
        const filenameText = document.getElementById('currentFilename');
        
        if (progressBar) {
            const percentValue = parseFloat(percent) || 0;
            progressBar.style.width = `${percentValue}%`;
            percentText.textContent = percent;
            speedText.textContent = `Speed: ${speed}`;
            etaText.textContent = `ETA: ${eta}`;
            filenameText.textContent = `Downloading: ${filename}`;
            
            // Show progress section if hidden
            document.getElementById('progressSection').style.display = 'block';
        }
    }

    handleDownloadComplete(data) {
        this.showSuccess(`Download completed: ${data.filename}`);
        this.hideProgress();
        this.removeFromDownloadsList(data.filename);
    }

    handleDownloadError(data) {
        this.showError(`Download failed: ${data.message}`);
        this.hideProgress();
    }

    async loadExistingDownloads() {
        try {
            const downloads = await window.electronAPI.getDownloadsList();
            if (downloads.length > 0) {
                this.showExistingDownloads(downloads);
            }
        } catch (error) {
            console.warn('Could not load existing downloads:', error);
        }
    }

    showExistingDownloads(files) {
        const container = document.getElementById('existingDownloads');
        if (!container) return;
        
        container.innerHTML = '<h3>Existing Downloads:</h3>';
        const list = document.createElement('ul');
        list.className = 'downloads-list';
        
        files.forEach(file => {
            const li = document.createElement('li');
            li.textContent = file;
            list.appendChild(li);
        });
        
        container.appendChild(list);
        container.style.display = 'block';
    }

    addToDownloadsList(filename, url) {
        const downloadsList = document.getElementById('downloadsList');
        if (!downloadsList) return;
        
        const item = document.createElement('div');
        item.className = 'download-item';
        item.id = `download-${filename}`;
        item.innerHTML = `
            <span>${filename}</span>
            <span class="status pending">Pending</span>
        `;
        
        downloadsList.prepend(item);
        this.currentDownloads.set(filename, { url, element: item });
    }

    removeFromDownloadsList(filename) {
        const element = document.getElementById(`download-${filename}`);
        if (element) {
            element.remove();
        }
        this.currentDownloads.delete(filename);
    }

    showLoadingState() {
        const btn = document.getElementById('downloadBtn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Starting...';
    }

    hideLoadingState() {
        const btn = document.getElementById('downloadBtn');
        btn.disabled = false;
        btn.textContent = 'Download Video';
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            ${type === 'success' ? '✓' : '✗'} ${message}
            <button class="close-btn">&times;</button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => notification.remove(), 5000);
        
        // Close button
        notification.querySelector('.close-btn').addEventListener('click', () => {
            notification.remove();
        });
    }

    clearForm() {
        document.getElementById('url').value = '';
        document.getElementById('filename').value = '';
    }

    hideProgress() {
        const progressSection = document.getElementById('progressSection');
        if (progressSection) {
            progressSection.style.display = 'none';
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new YouTubeDownloaderApp();
});