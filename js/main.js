// Main JavaScript for ClashBerry

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Add fade-in animation to cards
    animateCards();
    
    // Set up form validation
    setupFormValidation();
    
    // Initialize navigation
    setupNavigation();
    
    // Set up keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Performance monitoring
    logPerformance();
});

function initializeTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

function animateCards() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
}

function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const tagInput = form.querySelector('input[name*="tag"], input[id*="Tag"]');
            if (tagInput) {
                validateAndFormatTag(tagInput);
            }
        });
    });
}

function validateAndFormatTag(input) {
    let value = input.value.trim();
    
    // Remove any leading # characters
    value = value.replace(/^#+/, '');
    
    // Validate tag format (alphanumeric, specific length)
    if (value && !/^[A-Z0-9]+$/i.test(value)) {
        showAlert('Invalid tag format. Please use only letters and numbers.', 'warning');
        return false;
    }
    
    input.value = value;
    return true;
}

function setupNavigation() {
    // Add active class to current page nav link
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search focus
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="text"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('input[type="text"]:focus');
            if (searchInput) {
                searchInput.value = '';
                searchInput.blur();
            }
        }
    });
}

function showAlert(message, type = 'info', duration = 5000) {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert.position-fixed');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)}"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, duration);
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'primary': 'info-circle',
        'secondary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Utility functions
function formatNumber(num) {
    if (num === undefined || num === null) return '0';
    return new Intl.NumberFormat().format(num);
}

function formatPercentage(value, total) {
    if (!total || total === 0) return '0%';
    return ((value / total) * 100).toFixed(1) + '%';
}

function timeAgo(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Copied to clipboard!', 'success', 2000);
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showAlert('Copied to clipboard!', 'success', 2000);
    }
}

// Search history functionality
function saveSearchHistory(tag, type) {
    const historyKey = `search_history_${type}`;
    let history = JSON.parse(localStorage.getItem(historyKey) || '[]');
    
    if (!history.includes(tag)) {
        history.unshift(tag);
        if (history.length > 10) history.pop(); // Keep only last 10
        localStorage.setItem(historyKey, JSON.stringify(history));
    }
}

function getSearchHistory(type) {
    const historyKey = `search_history_${type}`;
    return JSON.parse(localStorage.getItem(historyKey) || '[]');
}

// Dark mode support
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Initialize dark mode from localStorage
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}

// Performance monitoring
function logPerformance() {
    if (window.performance) {
        window.addEventListener('load', () => {
            const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
            console.log(`Page load time: ${loadTime}ms`);
        });
    }
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Could send to logging service in production
});

// Page visibility API for pausing animations when tab is hidden
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Pause any running animations
        document.querySelectorAll('.progress-bar').forEach(bar => {
            bar.style.animationPlayState = 'paused';
        });
    } else {
        // Resume animations
        document.querySelectorAll('.progress-bar').forEach(bar => {
            bar.style.animationPlayState = 'running';
        });
    }
});

// Intersection Observer for scroll animations
function setupScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1
    });

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// Initialize scroll animations if elements exist
if (document.querySelectorAll('.animate-on-scroll').length > 0) {
    setupScrollAnimations();
}

// Service Worker registration for PWA (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment if you want to add PWA functionality
        // navigator.serviceWorker.register('/sw.js');
    });
}

// Export utilities for global use
window.cocUtils = {
    formatNumber,
    formatPercentage,
    timeAgo,
    copyToClipboard,
    showAlert,
    saveSearchHistory,
    getSearchHistory
};