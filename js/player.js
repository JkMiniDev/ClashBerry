// Player Search Functionality
document.addEventListener('DOMContentLoaded', function() {
    const playerSearchForm = document.getElementById('playerSearchForm');
    const playerTagInput = document.getElementById('playerTagInput');
    const searchBtn = document.getElementById('searchBtn');
    const resultsContainer = document.getElementById('resultsContainer');

    // Check for player tag in URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const playerTag = urlParams.get('tag');
    if (playerTag) {
        playerTagInput.value = playerTag;
        searchPlayer(playerTag);
    }

    // Handle form submission
    playerSearchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const tag = playerTagInput.value.trim();
        if (tag) {
            searchPlayer(tag);
        }
    });

    async function searchPlayer(playerTag) {
        try {
            // Update button state
            searchBtn.disabled = true;
            searchBtn.innerHTML = '<span class="spinner"></span> Searching...';

            // Show loading
            loadingUtils.showLoading('#resultsContainer');

            // Fetch player data
            const playerData = await cocAPI.getPlayer(playerTag);
            displayPlayerData(playerData);

        } catch (error) {
            loadingUtils.hideLoading();
            errorHandler.handleAPIError(error);
        } finally {
            // Reset button state
            searchBtn.disabled = false;
            searchBtn.innerHTML = '<i class="fas fa-search"></i> Search Player';
        }
    }

    function displayPlayerData(player) {
        loadingUtils.hideLoading();
        
        const html = `
            <!-- Player Overview -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card border-success">
                        <div class="card-header bg-success text-white">
                            <div class="row align-items-center">
                                <div class="col">
                                    <h4 class="mb-0">${player.name}</h4>
                                    <small>${player.tag}</small>
                                </div>
                                <div class="col-auto">
                                    <span class="badge bg-light text-dark fs-6">
                                        ${formatUtils.getTHIcon(player.townHallLevel)} ${player.townHallLevel}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6><i class="fas fa-info-circle text-success"></i> Player Information</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <td><strong>Experience Level:</strong></td>
                                            <td>${player.expLevel}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Trophies:</strong></td>
                                            <td>${formatUtils.formatNumber(player.trophies)}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Best Trophies:</strong></td>
                                            <td>${formatUtils.formatNumber(player.bestTrophies)}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>War Stars:</strong></td>
                                            <td>${player.warStars}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Attack Wins:</strong></td>
                                            <td>${formatUtils.formatNumber(player.attackWins)}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Defense Wins:</strong></td>
                                            <td>${formatUtils.formatNumber(player.defenseWins)}</td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6><i class="fas fa-trophy text-warning"></i> Additional Stats</h6>
                                    <table class="table table-sm">
                                        ${player.builderHallLevel ? `
                                        <tr>
                                            <td><strong>Builder Hall Level:</strong></td>
                                            <td>${player.builderHallLevel}</td>
                                        </tr>` : ''}
                                        ${player.versusTrophies ? `
                                        <tr>
                                            <td><strong>Versus Trophies:</strong></td>
                                            <td>${formatUtils.formatNumber(player.versusTrophies)}</td>
                                        </tr>` : ''}
                                        ${player.bestVersusTrophies ? `
                                        <tr>
                                            <td><strong>Best Versus Trophies:</strong></td>
                                            <td>${formatUtils.formatNumber(player.bestVersusTrophies)}</td>
                                        </tr>` : ''}
                                        <tr>
                                            <td><strong>Donations:</strong></td>
                                            <td>${formatUtils.formatNumber(player.donations)}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Donations Received:</strong></td>
                                            <td>${formatUtils.formatNumber(player.donationsReceived)}</td>
                                        </tr>
                                        ${player.clanCapitalContributions ? `
                                        <tr>
                                            <td><strong>Capital Contributions:</strong></td>
                                            <td>${formatUtils.formatNumber(player.clanCapitalContributions)}</td>
                                        </tr>` : ''}
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            ${renderClanInfo(player.clan, player.role)}
            ${renderLeagueInfo(player.league)}
            ${renderAchievements(player.achievements)}
            ${renderTroops(player.troops)}
            ${renderSpells(player.spells)}
            ${renderHeroes(player.heroes)}
        `;

        resultsContainer.innerHTML = html;
        animateProgressBars();
    }

    function renderClanInfo(clan, role) {
        if (!clan) return '';

        return `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-users"></i> Clan Information</h5>
                        </div>
                        <div class="card-body">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <h6>${clan.name}</h6>
                                    <p class="mb-1"><strong>Tag:</strong> ${clan.tag}</p>
                                    <p class="mb-1"><strong>Role:</strong> 
                                        <span class="badge ${formatUtils.getRoleBadgeClass(role)}">${role || 'Member'}</span>
                                    </p>
                                    <p class="mb-0"><strong>Clan Level:</strong> ${clan.clanLevel}</p>
                                </div>
                                <div class="col-md-4 text-end">
                                    <a href="clan.html?tag=${clan.tag.replace('#', '')}" 
                                       class="btn btn-primary">
                                        <i class="fas fa-users"></i> View Clan
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function renderLeagueInfo(league) {
        if (!league) return '';

        return `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-medal"></i> League Information</h5>
                        </div>
                        <div class="card-body">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <h6>${league.name}</h6>
                                    ${league.iconUrls && league.iconUrls.small ? 
                                        `<img src="${league.iconUrls.small}" alt="League Icon" class="league-icon">` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function renderAchievements(achievements) {
        if (!achievements || achievements.length === 0) return '';

        const achievementsHtml = achievements.slice(0, 12).map(achievement => {
            const progress = formatUtils.calculateProgress(achievement.value, achievement.target);
            return `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card h-100 achievement-card">
                        <div class="card-body p-3">
                            <h6 class="card-title">${achievement.name}</h6>
                            <div class="d-flex justify-content-between align-items-center">
                                <div class="flex-grow-1 me-2">
                                    <small class="text-muted d-block">${achievement.info}</small>
                                    <div class="progress mb-1" style="height: 6px;">
                                        <div class="progress-bar" role="progressbar" 
                                             style="width: ${progress}%" data-width="${progress}%"></div>
                                    </div>
                                    <small>${achievement.value}/${achievement.target}</small>
                                </div>
                                <div class="text-end">
                                    <span class="badge bg-primary achievement-stars">
                                        ${achievement.stars} <i class="fas fa-star"></i>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-trophy"></i> Achievements (${achievements.length})</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                ${achievementsHtml}
                            </div>
                            ${achievements.length > 12 ? `
                            <div class="text-center mt-3">
                                <button class="btn btn-outline-primary" onclick="showMoreAchievements()">
                                    Show More Achievements
                                </button>
                            </div>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function renderTroops(troops) {
        if (!troops || troops.length === 0) return '';

        const troopsHtml = troops.map(troop => {
            const progress = formatUtils.calculateProgress(troop.level, troop.maxLevel);
            return `
                <div class="col-md-6 col-lg-3 mb-3">
                    <div class="card text-center troop-card">
                        <div class="card-body p-2">
                            <h6 class="card-title">${troop.name}</h6>
                            <p class="mb-1 troop-level">Level ${troop.level}</p>
                            ${troop.maxLevel ? `<small class="text-muted max-level">Max: ${troop.maxLevel}</small>` : ''}
                            <div class="progress mt-1" style="height: 4px;">
                                <div class="progress-bar" role="progressbar" 
                                     style="width: ${progress}%" data-width="${progress}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-fist-raised"></i> Troops</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                ${troopsHtml}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function renderSpells(spells) {
        if (!spells || spells.length === 0) return '';

        const spellsHtml = spells.map(spell => {
            const progress = formatUtils.calculateProgress(spell.level, spell.maxLevel);
            return `
                <div class="col-md-6 col-lg-3 mb-3">
                    <div class="card text-center spell-card">
                        <div class="card-body p-2">
                            <h6 class="card-title">${spell.name}</h6>
                            <p class="mb-1 troop-level">Level ${spell.level}</p>
                            ${spell.maxLevel ? `<small class="text-muted max-level">Max: ${spell.maxLevel}</small>` : ''}
                            <div class="progress mt-1" style="height: 4px;">
                                <div class="progress-bar bg-info" role="progressbar" 
                                     style="width: ${progress}%" data-width="${progress}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-magic"></i> Spells</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                ${spellsHtml}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function renderHeroes(heroes) {
        if (!heroes || heroes.length === 0) return '';

        const heroesHtml = heroes.map(hero => {
            const progress = formatUtils.calculateProgress(hero.level, hero.maxLevel);
            return `
                <div class="col-md-6 col-lg-3 mb-3">
                    <div class="card text-center hero-card border-warning">
                        <div class="card-body p-2">
                            <h6 class="card-title text-warning">
                                <i class="fas fa-crown"></i> ${hero.name}
                            </h6>
                            <p class="mb-1 troop-level">Level ${hero.level}</p>
                            ${hero.maxLevel ? `<small class="text-muted max-level">Max: ${hero.maxLevel}</small>` : ''}
                            <div class="progress mt-1" style="height: 4px;">
                                <div class="progress-bar bg-warning" role="progressbar" 
                                     style="width: ${progress}%" data-width="${progress}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-crown"></i> Heroes</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                ${heroesHtml}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const targetWidth = bar.dataset.width || bar.style.width;
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.transition = 'width 1s ease-out';
                bar.style.width = targetWidth;
            }, 100);
        });
    }
});

// Show more achievements functionality
function showMoreAchievements() {
    // This could be expanded to show all achievements in a modal
    // For now, just show a message
    showToast('Feature coming soon: View all achievements', 'info');
}

// Toast notification function (if not already defined in clan.js)
function showToast(message, type = 'info') {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Create or get toast container
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast element after hiding
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}