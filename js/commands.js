// Discord Commands Data and Display
document.addEventListener('DOMContentLoaded', function() {
    const commandsList = document.getElementById('commandsList');
    
    // Discord commands data
    const discordCommands = [
        {
            name: '!clan',
            description: 'Display comprehensive clan information including member list, war stats, and clan details',
            usage: '!clan <clan_tag>',
            features: ['Clan overview', 'Member list with TH levels', 'War statistics', 'Clan type and requirements'],
            category: 'clan',
            example: '!clan #2Y9L0RYR0',
            webAlternative: true
        },
        {
            name: '!player',
            description: 'Show detailed player statistics, achievements, and troop information',
            usage: '!player <player_tag>',
            features: ['Player stats', 'Achievement progress', 'Troop levels', 'Clan information'],
            category: 'player',
            example: '!player #2PP',
            webAlternative: true
        },
        {
            name: '!war',
            description: 'Display current clan war information with attack details and member performance',
            usage: '!war <clan_tag>',
            features: ['War overview', 'Attack progress', 'Member performance', 'Star and destruction percentages'],
            category: 'war',
            example: '!war #2Y9L0RYR0',
            webAlternative: true
        },
        {
            name: '!linkaccount',
            description: 'Link your Discord account to your Clash of Clans player tag',
            usage: '!linkaccount <player_tag>',
            features: ['Account verification', 'Discord-COC linking', 'Profile management'],
            category: 'account',
            example: '!linkaccount #2PP',
            webAlternative: false
        },
        {
            name: '!addclan',
            description: 'Add a clan to the server\'s tracking system',
            usage: '!addclan <clan_tag>',
            features: ['Clan registration', 'Server clan list', 'Clan monitoring'],
            category: 'management',
            example: '!addclan #2Y9L0RYR0',
            webAlternative: false
        },
        {
            name: '!removeclan',
            description: 'Remove a clan from the server\'s tracking system',
            usage: '!removeclan <clan_tag>',
            features: ['Clan deregistration', 'Clean up clan list', 'Stop monitoring'],
            category: 'management',
            example: '!removeclan #2Y9L0RYR0',
            webAlternative: false
        },
        {
            name: '!accounts',
            description: 'View all linked accounts for a Discord user',
            usage: '!accounts [@user]',
            features: ['Account overview', 'Verification status', 'Multiple account support'],
            category: 'account',
            example: '!accounts @username',
            webAlternative: false
        },
        {
            name: '!unlinkaccount',
            description: 'Unlink a Discord account from a Clash of Clans player tag',
            usage: '!unlinkaccount <player_tag>',
            features: ['Account unlinking', 'Profile cleanup', 'Privacy management'],
            category: 'account',
            example: '!unlinkaccount #2PP',
            webAlternative: false
        },
        {
            name: '!help',
            description: 'Display help information and available commands',
            usage: '!help [command]',
            features: ['Command list', 'Usage instructions', 'Feature descriptions'],
            category: 'utility',
            example: '!help clan',
            webAlternative: false
        }
    ];
    
    // Render commands
    displayCommands(discordCommands);
    
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
                                            '<span class="text-muted small">Discord only</span>'}
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
            'account': 'fas fa-id-card',
            'management': 'fas fa-cogs',
            'utility': 'fas fa-question-circle'
        };
        return icons[category] || 'fas fa-terminal';
    }
    
    function getCategoryColor(category) {
        const colors = {
            'clan': 'text-primary',
            'player': 'text-success',
            'war': 'text-warning',
            'account': 'text-info',
            'management': 'text-secondary',
            'utility': 'text-dark'
        };
        return colors[category] || 'text-dark';
    }
    
    function getExampleDescription(category) {
        const descriptions = {
            'clan': 'Shows comprehensive clan information including members and war status',
            'player': 'Displays detailed player statistics and progression',
            'war': 'Shows current war status and attack progress',
            'account': 'Links or manages Discord account connections',
            'management': 'Manages server clan settings and tracking',
            'utility': 'Provides help and utility functions'
        };
        return descriptions[category] || 'Executes the specified command';
    }
    
    function getWebAlternative(category) {
        const alternatives = {
            'clan': `
                <a href="clan.html" class="btn btn-sm btn-outline-primary">
                    <i class="fas fa-users"></i> Use Clan Search
                </a>
            `,
            'player': `
                <a href="player.html" class="btn btn-sm btn-outline-success">
                    <i class="fas fa-user"></i> Use Player Search
                </a>
            `,
            'war': `
                <a href="clan.html" class="btn btn-sm btn-outline-warning">
                    <i class="fas fa-sword"></i> View War Data
                </a>
            `
        };
        return alternatives[category] || '<span class="text-muted small">Not available</span>';
    }
});