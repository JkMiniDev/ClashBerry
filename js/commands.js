// ClashBerry Features Data and Display
document.addEventListener('DOMContentLoaded', function() {
    const commandsList = document.getElementById('commandsList');
    
    // ClashBerry features data
    const clashberryFeatures = [
        {
            name: 'Clan Analytics',
            description: 'Display comprehensive clan information including member list, war stats, and clan details',
            usage: 'Enter clan tag in search',
            features: ['Clan overview', 'Member list with TH levels', 'War statistics', 'Clan type and requirements'],
            category: 'clan',
            example: 'Search: #2Y9L0RYR0',
            webAlternative: true
        },
        {
            name: 'Player Statistics',
            description: 'Show detailed player statistics, achievements, and troop information',
            usage: 'Enter player tag in search',
            features: ['Player stats', 'Achievement progress', 'Troop levels', 'Clan information'],
            category: 'player',
            example: 'Search: #2PP',
            webAlternative: true
        },
        {
            name: 'War Tracking',
            description: 'Display current clan war information with attack details and member performance',
            usage: 'Available in clan search results',
            features: ['War overview', 'Attack progress', 'Member performance', 'Star and destruction percentages'],
            category: 'war',
            example: 'Included with clan data',
            webAlternative: true
        },
        {
            name: 'Real-time Data',
            description: 'Access up-to-date Clash of Clans data directly from official API',
            usage: 'Automatic with all searches',
            features: ['Live statistics', 'Current trophies', 'Latest war status', 'Real-time clan info'],
            category: 'data',
            example: 'Always current data',
            webAlternative: true
        },
        {
            name: 'Search History',
            description: 'Keep track of recently searched clans and players for quick access',
            usage: 'Automatic local storage',
            features: ['Recent searches', 'Quick access', 'Local storage', 'Search suggestions'],
            category: 'utility',
            example: 'Previous searches saved',
            webAlternative: true
        },
        {
            name: 'Responsive Design',
            description: 'Access ClashBerry on any device with full functionality',
            usage: 'Works on all devices',
            features: ['Mobile friendly', 'Tablet optimized', 'Desktop experience', 'Touch friendly'],
            category: 'design',
            example: 'Any device compatibility',
            webAlternative: true
        },
        {
            name: 'Advanced Analytics',
            description: 'Deep dive into clan and player statistics with detailed analysis',
            usage: 'Available in search results',
            features: ['Detailed breakdowns', 'Progress tracking', 'Performance metrics', 'Trend analysis'],
            category: 'analytics',
            example: 'Comprehensive stat views',
            webAlternative: true
        },
        {
            name: 'Fast Performance',
            description: 'Optimized loading and responsive interface for quick data access',
            usage: 'Built-in optimization',
            features: ['Quick loading', 'Efficient API calls', 'Cached assets', 'Smooth animations'],
            category: 'performance',
            example: 'Sub-second load times',
            webAlternative: true
        },
        {
            name: 'User Friendly',
            description: 'Intuitive interface designed for easy navigation and data discovery',
            usage: 'Easy to use interface',
            features: ['Clean design', 'Clear navigation', 'Helpful tooltips', 'Error guidance'],
            category: 'usability',
            example: 'Simple and effective',
            webAlternative: true
        }
    ];
    
    // Render features
    displayCommands(clashberryFeatures);
    
    function displayCommands(commands) {
        const commandsHtml = commands.map(command => {
            const iconClass = getCategoryIcon(command.category);
            const iconColor = getCategoryColor(command.category);
            
            return `
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card h-100 command-card">
                            <div class="card-header">
                                <div class="row align-items-center">
                                    <div class="col">
                                        <h5 class="mb-0">
                                            <span class="command-name">${command.name}</span>
                                        </h5>
                                        <small class="text-muted">${command.description}</small>
                                    </div>
                                    <div class="col-auto">
                                        <i class="${iconClass} ${iconColor} fa-2x"></i>
                                    </div>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-terminal"></i> Usage</h6>
                                        <div class="code-block mb-3">${command.usage}</div>
                                        
                                        <h6><i class="fas fa-star"></i> Features</h6>
                                        <ul class="list-unstyled">
                                            ${command.features.map(feature => 
                                                `<li><i class="fas fa-check text-success"></i> ${feature}</li>`
                                            ).join('')}
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-play-circle"></i> Example</h6>
                                        <div class="code-block mb-3">${command.example}</div>
                                        <small class="text-muted d-block mb-3">${getExampleDescription(command.category)}</small>
                                        
                                        <h6><i class="fas fa-external-link-alt"></i> Web Alternative</h6>
                                        ${command.webAlternative ? getWebAlternative(command.category) : 
                                            '<span class="text-muted small">Not available</span>'}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        commandsList.innerHTML = commandsHtml;
    }
    
    function getCategoryIcon(category) {
        const icons = {
            'clan': 'fas fa-users',
            'player': 'fas fa-user',
            'war': 'fas fa-sword',
            'data': 'fas fa-database',
            'utility': 'fas fa-tools',
            'design': 'fas fa-mobile-alt',
            'analytics': 'fas fa-chart-line',
            'performance': 'fas fa-rocket',
            'usability': 'fas fa-heart'
        };
        return icons[category] || 'fas fa-star';
    }
    
    function getCategoryColor(category) {
        const colors = {
            'clan': 'text-primary',
            'player': 'text-success',
            'war': 'text-warning',
            'data': 'text-info',
            'utility': 'text-secondary',
            'design': 'text-purple',
            'analytics': 'text-dark',
            'performance': 'text-danger',
            'usability': 'text-pink'
        };
        return colors[category] || 'text-dark';
    }
    
    function getExampleDescription(category) {
        const descriptions = {
            'clan': 'Shows comprehensive clan information including members and war status',
            'player': 'Displays detailed player statistics and progression',
            'war': 'Shows current war status and attack progress',
            'data': 'Provides real-time data from Clash of Clans API',
            'utility': 'Enhances user experience with helpful features',
            'design': 'Optimized for all devices and screen sizes',
            'analytics': 'Deep analysis of statistics and trends',
            'performance': 'Fast and efficient data processing',
            'usability': 'Designed for ease of use and accessibility'
        };
        return descriptions[category] || 'Available throughout the ClashBerry platform';
    }
    
    function getWebAlternative(category) {
        const alternatives = {
            'clan': `
                <a href="clan.html" class="btn btn-sm btn-outline-primary">
                    <i class="fas fa-users"></i> Try Clan Search
                </a>
            `,
            'player': `
                <a href="player.html" class="btn btn-sm btn-outline-success">
                    <i class="fas fa-user"></i> Try Player Search
                </a>
            `,
            'war': `
                <a href="clan.html" class="btn btn-sm btn-outline-warning">
                    <i class="fas fa-sword"></i> View War Data
                </a>
            `,
            'data': `
                <span class="badge bg-info">
                    <i class="fas fa-check"></i> Built-in Feature
                </span>
            `,
            'utility': `
                <span class="badge bg-secondary">
                    <i class="fas fa-check"></i> Available Now
                </span>
            `,
            'design': `
                <span class="badge bg-purple">
                    <i class="fas fa-check"></i> Responsive Design
                </span>
            `,
            'analytics': `
                <span class="badge bg-dark">
                    <i class="fas fa-check"></i> Advanced Stats
                </span>
            `,
            'performance': `
                <span class="badge bg-danger">
                    <i class="fas fa-check"></i> Optimized
                </span>
            `,
            'usability': `
                <span class="badge bg-pink">
                    <i class="fas fa-check"></i> User Friendly
                </span>
            `
        };
        return alternatives[category] || '<span class="text-muted small">Not available</span>';
    }
});