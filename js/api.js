// API Configuration for Custom Proxy
const API_CONFIG = {
    baseURL: 'https://api.jktripuri.site',
    token: 'JkMiniDev%1998'
};

// API Helper Functions
class COCAPI {
    constructor() {
        this.baseURL = API_CONFIG.baseURL;
        this.token = API_CONFIG.token;
    }

    // Generic API request method
    async makeRequest(endpoint) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            console.log('Making API request to:', url); // Debug log
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server responded with ${response.status}: ${errorText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Format clan tag for API - exactly like working HTML
    formatClanTag(tag) {
        if (!tag) return '';
        // If tag doesn't start with #, add it first, then replace with %23
        const tagWithHash = tag.startsWith('#') ? tag : '#' + tag;
        return tagWithHash.replace("#", "%23");
    }

    // Format player tag for API - exactly like working HTML  
    formatPlayerTag(tag) {
        if (!tag) return '';
        // If tag doesn't start with #, add it first, then replace with %23
        const tagWithHash = tag.startsWith('#') ? tag : '#' + tag;
        return tagWithHash.replace("#", "%23");
    }

    // Get clan information
    async getClan(clanTag) {
        const formattedTag = this.formatClanTag(clanTag);
        return await this.makeRequest(`/clans/${formattedTag}`);
    }

    // Get player information
    async getPlayer(playerTag) {
        const formattedTag = this.formatPlayerTag(playerTag);
        return await this.makeRequest(`/players/${formattedTag}`);
    }

    // Get current clan war
    async getClanWar(clanTag) {
        const formattedTag = this.formatClanTag(clanTag);
        return await this.makeRequest(`/clans/${formattedTag}/currentwar`);
    }

    // Get CWL group information
    async getCWLGroup(clanTag) {
        const formattedTag = this.formatClanTag(clanTag);
        return await this.makeRequest(`/clans/${formattedTag}/currentwar/leaguegroup`);
    }

    // Get clan war log
    async getClanWarLog(clanTag) {
        const formattedTag = this.formatClanTag(clanTag);
        return await this.makeRequest(`/clans/${formattedTag}/warlog`);
    }

    // Get clan members
    async getClanMembers(clanTag) {
        const formattedTag = this.formatClanTag(clanTag);
        return await this.makeRequest(`/clans/${formattedTag}/members`);
    }
}

// Create global API instance
const cocAPI = new COCAPI();

// Utility functions for data formatting
const formatUtils = {
    // Format numbers with commas
    formatNumber(num) {
        if (num === undefined || num === null) return '0';
        return new Intl.NumberFormat().format(num);
    },

    // Format percentage
    formatPercentage(value, total) {
        if (!total || total === 0) return '0%';
        return ((value / total) * 100).toFixed(1) + '%';
    },

    // Format date
    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    },

    // Get time ago
    timeAgo(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
        return `${Math.floor(diffDays / 30)} months ago`;
    },

    // Format clan type
    formatClanType(type) {
        const types = {
            'open': 'Anyone Can Join',
            'inviteOnly': 'Invite Only',
            'closed': 'Closed'
        };
        return types[type] || type;
    },

    // Format war state
    formatWarState(state) {
        const states = {
            'notInWar': 'Not in War',
            'preparation': 'Preparation',
            'inWar': 'In War',
            'warEnded': 'War Ended'
        };
        return states[state] || state;
    },

    // Get role badge class
    getRoleBadgeClass(role) {
        const roleClasses = {
            'leader': 'bg-danger',
            'coLeader': 'bg-warning',
            'elder': 'bg-info',
            'member': 'bg-secondary'
        };
        return roleClasses[role] || 'bg-secondary';
    },

    // Get TH emoji/icon
    getTHIcon(level) {
        // You can replace this with actual emoji mappings if available
        return `TH${level}`;
    },

    // Calculate progress percentage
    calculateProgress(current, max) {
        if (!max || max === 0) return 0;
        return Math.min((current / max) * 100, 100);
    }
};

// Error handling utilities
const errorHandler = {
    // Show error message to user
    showError(message, container = 'main') {
        const errorHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-triangle"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const targetContainer = document.querySelector(container);
        if (targetContainer) {
            targetContainer.insertAdjacentHTML('afterbegin', errorHtml);
        }
    },

    // Handle API errors
    handleAPIError(error) {
        let message = 'An error occurred while fetching data.';
        
        if (error.message.includes('404')) {
            message = 'Clan or player not found. Please check the tag and try again.';
        } else if (error.message.includes('403')) {
            message = 'Access denied. Please check API configuration.';
        } else if (error.message.includes('429')) {
            message = 'Too many requests. Please wait a moment and try again.';
        } else if (error.message.includes('500')) {
            message = 'Server error. Please try again later.';
        }
        
        this.showError(message);
        console.error('API Error:', error);
    }
};

// Loading state utilities
const loadingUtils = {
    // Show loading spinner
    showLoading(container) {
        const loadingHtml = `
            <div class="d-flex justify-content-center py-5" id="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span class="ms-2">Loading data...</span>
            </div>
        `;
        
        const targetContainer = document.querySelector(container);
        if (targetContainer) {
            targetContainer.innerHTML = loadingHtml;
        }
    },

    // Hide loading spinner
    hideLoading() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { cocAPI, formatUtils, errorHandler, loadingUtils };
}