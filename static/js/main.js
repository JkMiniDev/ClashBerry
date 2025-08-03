// Main JavaScript for COC Bot Portal

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Form validation and enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const tagInput = form.querySelector('input[name="tag"]');
            if (tagInput) {
                validateAndFormatTag(tagInput);
            }
            
            // Add loading state to submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner"></span> Searching...';
            }
        });
    });

    // Search functionality enhancements
    setupSearchEnhancements();
    
    // Table enhancements
    setupTableEnhancements();
    
    // Member list interactions
    setupMemberListInteractions();
    
    // Achievement progress animations
    animateProgressBars();
    
    // Copy functionality for tags
    setupCopyFunctionality();
});

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

function setupSearchEnhancements() {
    // Add search history functionality
    const searchInputs = document.querySelectorAll('input[name="tag"]');
    searchInputs.forEach(input => {
        // Load search history
        const historyKey = `search_history_${input.closest('form').action.split('/').pop()}`;
        const history = JSON.parse(localStorage.getItem(historyKey) || '[]');
        
        // Add datalist for autocomplete
        const datalist = document.createElement('datalist');
        datalist.id = `${input.name}_history`;
        history.forEach(tag => {
            const option = document.createElement('option');
            option.value = tag;
            datalist.appendChild(option);
        });
        document.body.appendChild(datalist);
        input.setAttribute('list', datalist.id);
        
        // Save to history on form submit
        input.closest('form').addEventListener('submit', function() {
            if (input.value && !history.includes(input.value)) {
                history.unshift(input.value);
                if (history.length > 10) history.pop(); // Keep only last 10
                localStorage.setItem(historyKey, JSON.stringify(history));
            }
        });
    });
}

function setupTableEnhancements() {
    // Add sorting functionality to tables
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (header.textContent.trim() && index > 0) { // Skip first column (rank)
                header.style.cursor = 'pointer';
                header.title = 'Click to sort';
                header.addEventListener('click', () => sortTable(table, index));
            }
        });
    });
}

function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isNumeric = rows.every(row => {
        const cell = row.cells[columnIndex];
        const text = cell.textContent.replace(/[,\s]/g, '');
        return !isNaN(text) && text !== '';
    });
    
    const sortedRows = rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        
        if (isNumeric) {
            return parseInt(bText.replace(/[,\s]/g, '')) - parseInt(aText.replace(/[,\s]/g, ''));
        } else {
            return aText.localeCompare(bText);
        }
    });
    
    // Clear and re-add rows
    tbody.innerHTML = '';
    sortedRows.forEach(row => tbody.appendChild(row));
    
    // Add visual feedback
    showAlert('Table sorted successfully', 'success', 2000);
}

function setupMemberListInteractions() {
    // Add click-to-copy functionality for player tags
    const memberRows = document.querySelectorAll('.table tbody tr');
    memberRows.forEach(row => {
        const tagCell = row.querySelector('td:nth-child(2) small');
        if (tagCell) {
            tagCell.style.cursor = 'pointer';
            tagCell.title = 'Click to copy tag';
            tagCell.addEventListener('click', function() {
                copyToClipboard(this.textContent);
                showAlert('Player tag copied to clipboard!', 'info', 2000);
            });
        }
    });
}

function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-out';
            bar.style.width = targetWidth;
        }, 100);
    });
}

function setupCopyFunctionality() {
    // Add copy buttons to clan and player tags
    const tags = document.querySelectorAll('small:contains("#")');
    tags.forEach(tag => {
        if (tag.textContent.includes('#')) {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'btn btn-sm btn-outline-secondary ms-2';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.title = 'Copy tag';
            copyBtn.addEventListener('click', function(e) {
                e.preventDefault();
                copyToClipboard(tag.textContent);
                showAlert('Tag copied to clipboard!', 'info', 2000);
            });
            tag.appendChild(copyBtn);
        }
    });
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    }
}

function showAlert(message, type = 'info', duration = 5000) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        ${message}
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

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatPercentage(value, total) {
    return ((value / total) * 100).toFixed(1) + '%';
}

function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
}

// Dark mode toggle (if needed in future)
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
        const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log(`Page load time: ${loadTime}ms`);
    }
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Could send to logging service in production
});

// API call helper
async function apiCall(endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showAlert('Failed to fetch data. Please try again.', 'danger');
        throw error;
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search focus
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="tag"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
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

// Log page load completion
window.addEventListener('load', logPerformance);