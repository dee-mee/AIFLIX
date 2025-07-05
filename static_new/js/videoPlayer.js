class VideoPlayerControls {
    constructor(playerId) {
        this.player = document.getElementById(playerId);
        if (!this.player) {
            console.error('Video player element not found with ID:', playerId);
            return;
        }
        
        this.subtitleBtn = document.getElementById('subtitleBtn');
        this.subtitleMenu = document.getElementById('subtitleMenu');
        this.tracks = [];
        
        console.log('Initializing video player controls');
        console.log('Subtitle button:', this.subtitleBtn);
        console.log('Subtitle menu:', this.subtitleMenu);
        
        this.setupEventListeners();
        this.setupShortcutHelp();
        this.setupSubtitles();
    }

    setupEventListeners() {
        // Prevent spacebar from scrolling the page when video is focused
        this.player.addEventListener('keydown', (e) => {
            if (e.code === 'Space' || e.code === 'ArrowUp' || e.code === 'ArrowDown') {
                e.preventDefault();
            }
        });

        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Only trigger if not in an input field
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            switch(e.code) {
                case 'Space':
                    e.preventDefault();
                    this.togglePlayPause();
                    break;
                case 'ArrowLeft':
                    this.seek(-10);
                    break;
                case 'ArrowRight':
                    this.seek(10);
                    break;
                case 'ArrowUp':
                    this.adjustVolume(0.1);
                    break;
                case 'ArrowDown':
                    this.adjustVolume(-0.1);
                    break;
                case 'KeyF':
                    this.toggleFullscreen();
                    break;
                case 'KeyM':
                    this.toggleMute();
                    break;
                case 'KeyC':
                    this.toggleCaptions();
                    break;
                case 'Slash':
                    if (e.shiftKey) this.toggleHelp();
                    break;
            }
        });
    }

    togglePlayPause() {
        if (this.player.paused) {
            this.player.play();
            this.showFeedback('▶️ Play');
        } else {
            this.player.pause();
            this.showFeedback('⏸ Pause');
        }
    }

    seek(seconds) {
        this.player.currentTime += seconds;
        this.showFeedback(seconds > 0 ? `⏩ +${seconds}s` : `⏪ ${seconds}s`);
    }

    adjustVolume(change) {
        const newVolume = Math.min(1, Math.max(0, this.player.volume + change));
        this.player.volume = newVolume;
        this.showFeedback(`🔊 ${Math.round(newVolume * 100)}%`);
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.player.requestFullscreen().catch(err => {
                console.error('Error attempting to enable fullscreen:', err);
            });
            this.showFeedback('⛶ Fullscreen');
        } else {
            document.exitFullscreen();
            this.showFeedback('⛶ Exit Fullscreen');
        }
    }

    toggleMute() {
        this.player.muted = !this.player.muted;
        this.showFeedback(this.player.muted ? '🔇 Muted' : '🔊 Unmuted');
    }

    setupSubtitles() {
        if (!this.player) {
            console.error('Cannot setup subtitles: video player not found');
            return;
        }
        
        // Get all text tracks
        this.tracks = Array.from(this.player.textTracks || []);
        console.log('Found text tracks:', this.tracks);
        
        // Hide all tracks by default
        this.tracks.forEach((track, index) => {
            console.log(`Track ${index}:`, {
                kind: track.kind,
                label: track.label,
                language: track.language,
                mode: track.mode,
                cues: track.cues ? track.cues.length : 0
            });
            track.mode = 'hidden';
        });
        
        // Set up subtitle menu
        if (this.subtitleMenu) {
            const options = this.subtitleMenu.querySelectorAll('.subtitle-option');
            
            options.forEach(option => {
                option.addEventListener('click', () => {
                    const lang = option.getAttribute('data-lang');
                    this.setSubtitle(lang);
                    this.subtitleMenu.classList.remove('show');
                });
            });
        }
        
        // Toggle menu on button click
        if (this.subtitleBtn) {
            this.subtitleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.subtitleMenu.classList.toggle('show');
            });
        }
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (this.subtitleMenu && !this.subtitleMenu.contains(e.target) && 
                this.subtitleBtn && !this.subtitleBtn.contains(e.target)) {
                this.subtitleMenu.classList.remove('show');
            }
        });
    }
    
    setSubtitle(lang) {
        // Hide all tracks
        this.tracks.forEach(track => {
            track.mode = 'hidden';
        });
        
        if (lang === 'off') {
            this.showFeedback('📝 Subtitles Off');
            return;
        }
        
        // Find and show the selected track
        const track = this.tracks.find(t => t.language === lang);
        if (track) {
            track.mode = 'showing';
            this.showFeedback(`📝 ${this.getLanguageName(lang)}`);
            
            // Update active state in menu
            const options = this.subtitleMenu.querySelectorAll('.subtitle-option');
            options.forEach(opt => {
                if (opt.getAttribute('data-lang') === lang) {
                    opt.classList.add('active');
                } else {
                    opt.classList.remove('active');
                }
            });
        }
    }
    
    getLanguageName(code) {
        const langNames = new Intl.DisplayNames(['en'], {type: 'language'});
        try {
            return langNames.of(code) || code.toUpperCase();
        } catch (e) {
            return code.toUpperCase();
        }
    }
    
    toggleCaptions() {
        if (!this.subtitleMenu) return;
        
        // Show menu if hidden
        if (!this.subtitleMenu.classList.contains('show')) {
            this.subtitleMenu.classList.add('show');
            return;
        }
        
        // Toggle between subtitle tracks if menu is already visible
        const options = Array.from(this.subtitleMenu.querySelectorAll('.subtitle-option'));
        if (options.length <= 1) return;
        
        const currentIndex = options.findIndex(opt => opt.classList.contains('active'));
        const nextIndex = (currentIndex + 1) % options.length;
        const nextLang = options[nextIndex].getAttribute('data-lang');
        
        this.setSubtitle(nextLang);
    }

    showFeedback(message) {
        // Remove existing feedback if any
        let feedback = document.querySelector('.video-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'video-feedback';
            document.body.appendChild(feedback);
        }
        
        feedback.textContent = message;
        feedback.style.opacity = '1';
        
        // Hide after delay
        clearTimeout(this.feedbackTimeout);
        this.feedbackTimeout = setTimeout(() => {
            feedback.style.opacity = '0';
        }, 1500);
    }

    setupShortcutHelp() {
        const helpContent = `
            <div class="shortcut-help">
                <h3>Keyboard Shortcuts</h3>
                <ul>
                    <li><kbd>Space</kbd> Play/Pause</li>
                    <li><kbd>←</kbd> <kbd>→</kbd> Seek -10s / +10s</li>
                    <li><kbd>↑</kbd> <kbd>↓</kbd> Volume</li>
                    <li><kbd>F</kbd> Toggle Fullscreen</li>
                    <li><kbd>M</kbd> Mute/Unmute</li>
                    <li><kbd>C</kbd> Toggle Captions</li>
                    <li><kbd>?</kbd> Show/Hide Help</li>
                </ul>
                <button class="close-help">Close</button>
            </div>
        `;

        const helpButton = document.createElement('button');
        helpButton.className = 'help-button';
        helpButton.innerHTML = '?';
        helpButton.title = 'Show Keyboard Shortcuts (?)';
        helpButton.addEventListener('click', () => this.toggleHelp());
        
        // Add to player controls or body
        const controls = this.player.parentElement.querySelector('.video-controls');
        if (controls) {
            controls.appendChild(helpButton);
        } else {
            document.body.appendChild(helpButton);
        }

        // Add help dialog
        const helpDialog = document.createElement('div');
        helpDialog.className = 'shortcut-help-dialog';
        helpDialog.style.display = 'none';
        helpDialog.innerHTML = helpContent;
        document.body.appendChild(helpDialog);

        // Close button
        helpDialog.querySelector('.close-help').addEventListener('click', () => {
            helpDialog.style.display = 'none';
        });

        // Toggle help with ?
        this.toggleHelp = () => {
            helpDialog.style.display = helpDialog.style.display === 'none' ? 'block' : 'none';
        };
    }
}

// Initialize when DOM is fully loaded and video element is ready
function initVideoPlayer() {
    const videoPlayer = document.getElementById('videoPlayer');
    if (!videoPlayer) {
        console.error('Video player element not found with ID: videoPlayer');
        return;
    }

    // Remove any existing controls to prevent conflicts
    videoPlayer.removeAttribute('controls');
    
    console.log('Initializing video player with ID:', 'videoPlayer');
    
    const initControls = () => {
        // Only initialize if not already initialized
        if (!videoPlayer._playerControls) {
            videoPlayer._playerControls = new VideoPlayerControls('videoPlayer');
            console.log('Video player controls initialized');
        }
    };
    
    if (videoPlayer.readyState >= 2) {  // HAVE_CURRENT_DATA
        initControls();
    } else {
        const onLoaded = () => {
            console.log('Video metadata loaded, initializing controls');
            initControls();
            videoPlayer.removeEventListener('loadedmetadata', onLoaded);
        };
        videoPlayer.addEventListener('loadedmetadata', onLoaded);
    }
}

// Try to initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Remove any existing event listeners that might interfere
    const videoPlayer = document.getElementById('videoPlayer');
    if (videoPlayer) {
        videoPlayer.onplay = null;
        videoPlayer.onpause = null;
        videoPlayer.onseeking = null;
    }
    
    // Initialize our controls
    initVideoPlayer();
});

// Also try to initialize when the window loads (as a fallback)
window.addEventListener('load', initVideoPlayer);
