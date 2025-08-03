// Clan Search Functionality
document.addEventListener('DOMContentLoaded', function() {
    const clanSearchForm = document.getElementById('clanSearchForm');
    const clanTagInput = document.getElementById('clanTagInput');
    const searchBtn = document.getElementById('searchBtn');
    const resultsContainer = document.getElementById('resultsContainer');

    // Check for clan tag in URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const clanTag = urlParams.get('tag');
    if (clanTag) {
        clanTagInput.value = clanTag;
        searchClan(clanTag);
    }

    // Handle form submission
    clanSearchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const tag = clanTagInput.value.trim();
        if (tag) {
            searchClan(tag);
        }
    });

    async function searchClan(clanTag) {
        try {
            // Update button state
            searchBtn.disabled = true;
            searchBtn.innerHTML = '<span class="spinner"></span> Searching...';

            // Show loading
            loadingUtils.showLoading('#resultsContainer');

            // Debug log
            console.log('Searching for clan:', clanTag);

            // Fetch clan data
            const [clanData, warData, cwlData] = await Promise.allSettled([
                cocAPI.getClan(clanTag),
                cocAPI.getClanWar(clanTag).catch(() => null),
                cocAPI.getCWLGroup(clanTag).catch(() => null)
            ]);

            // Handle clan data result
            if (clanData.status === 'fulfilled') {
                console.log('Clan data received:', clanData.value);
                displayClanData(clanData.value, 
                    warData.status === 'fulfilled' ? warData.value : null,
                    cwlData.status === 'fulfilled' ? cwlData.value : null);
            } else {
                throw clanData.reason;
            }

        } catch (error) {
            loadingUtils.hideLoading();
            console.error('Search error:', error);
            
            // Show detailed error message
            resultsContainer.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <h5><i class="fas fa-exclamation-triangle"></i> Error fetching clan data</h5>
                    <p><strong>Error:</strong> ${error.message}</p>
                    <hr>
                    <p class="mb-0">
                        <strong>Please check:</strong><br>
                        1. You entered a valid clan tag (e.g. #ABC123)<br>
                        2. The clan exists<br>
                        3. Try again in a moment
                    </p>
                </div>
            `;
        } finally {
            // Reset button state
            searchBtn.disabled = false;
            searchBtn.innerHTML = '<i class="fas fa-search"></i> Search Clan';
        }
    }

    function displayClanData(clan, war, cwl) {
        loadingUtils.hideLoading();
        
        const html = `
            <!-- Clan Overview -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card border-primary">
                        <div class="card-header bg-primary text-white">
                            <div class="row align-items-center">
                                <div class="col">
                                    <h4 class="mb-0">${clan.name}</h4>
                                    <small>${clan.tag}</small>
                                </div>
                                <div class="col-auto">
                                    ${clan.badgeUrls && clan.badgeUrls.large ? 
                                        `<img src="${clan.badgeUrls.large}" alt="Clan Badge" class="clan-badge">` : 
                                        '<i class="fas fa-shield-alt fa-3x"></i>'}
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6><i class="fas fa-info-circle text-primary"></i> Clan Information</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <td><strong>Level:</strong></td>
                                            <td>${clan.clanLevel}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Members:</strong></td>
                                            <td>${clan.members}/50</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Required Trophies:</strong></td>
                                            <td>${formatUtils.formatNumber(clan.requiredTrophies)}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Type:</strong></td>
                                            <td><span class="badge clan-type-${clan.type}">${formatUtils.formatClanType(clan.type)}</span></td>
                                        </tr>
                                        <tr>
                                            <td><strong>Location:</strong></td>
                                            <td>${clan.location ? clan.location.name : 'International'}</td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6><i class="fas fa-trophy text-warning"></i> Clan Statistics</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <td><strong>Clan Points:</strong></td>
                                            <td>${formatUtils.formatNumber(clan.clanPoints)}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Versus Points:</strong></td>
                                            <td>${formatUtils.formatNumber(clan.clanVersusPoints)}</td>
                                        </tr>
                                        ${clan.warLeague ? `
                                        <tr>
                                            <td><strong>War League:</strong></td>
                                            <td>${clan.warLeague.name}</td>
                                        </tr>` : ''}
                                        <tr>
                                            <td><strong>War Wins:</strong></td>
                                            <td>${clan.warWins || 0}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>War Win Streak:</strong></td>
                                            <td>${clan.warWinStreak || 0}</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                            ${clan.description ? `
                            <div class="mt-3">
                                <h6><i class="fas fa-align-left text-info"></i> Description</h6>
                                <p class="text-muted">${clan.description}</p>
                            </div>` : ''}
                        </div>
                    </div>
                </div>
            </div>

            ${renderMembersList(clan.memberList)}
            ${renderWarData(war)}
            ${renderCWLData(cwl)}
        `;

        resultsContainer.innerHTML = html;
    }

    function renderMembersList(members) {
        if (!members || members.length === 0) return '';

        const membersHtml = members.map(member => `
            <tr>
                <td>${member.clanRank}</td>
                <td>
                    <a href="player.html?tag=${member.tag.replace('#', '')}" 
                       class="text-decoration-none member-tag">
                        ${member.name}
                    </a>
                    <br><small class="text-muted">${member.tag}</small>
                </td>
                <td>
                    <span class="badge ${formatUtils.getRoleBadgeClass(member.role)}">${member.role}</span>
                </td>
                <td>
                    ${formatUtils.getTHIcon(member.townHallLevel)} ${member.townHallLevel}
                </td>
                <td>${formatUtils.formatNumber(member.trophies)}</td>
                <td>${formatUtils.formatNumber(member.donations)}</td>
                <td>${formatUtils.formatNumber(member.donationsReceived)}</td>
            </tr>
        `).join('');

        return `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-users"></i> Clan Members (${members.length})</h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <thead class="table-dark">
                                        <tr>
                                            <th onclick="sortTable(this, 0)">Rank</th>
                                            <th onclick="sortTable(this, 1)">Name</th>
                                            <th onclick="sortTable(this, 2)">Role</th>
                                            <th onclick="sortTable(this, 3)">TH Level</th>
                                            <th onclick="sortTable(this, 4)">Trophies</th>
                                            <th onclick="sortTable(this, 5)">Donations</th>
                                            <th onclick="sortTable(this, 6)">Received</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${membersHtml}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function renderWarData(war) {
        if (!war || war.state === 'notInWar') return '';

        return `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card war-card">
                        <div class="card-header bg-warning text-dark">
                            <h5 class="mb-0"><i class="fas fa-sword"></i> Current War</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="war-stats">
                                        <h6>${war.clan.name}</h6>
                                        <p class="mb-1">Stars: ${war.clan.stars}/${war.teamSize * 3}</p>
                                        <p class="mb-1">Destruction: ${war.clan.destructionPercentage?.toFixed(1) || 0}%</p>
                                        <p class="mb-1">Attacks Used: ${war.clan.attacks || 0}/${war.teamSize * 2}</p>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="war-stats">
                                        <h6>${war.opponent.name}</h6>
                                        <p class="mb-1">Stars: ${war.opponent.stars}/${war.teamSize * 3}</p>
                                        <p class="mb-1">Destruction: ${war.opponent.destructionPercentage?.toFixed(1) || 0}%</p>
                                        <p class="mb-1">Attacks Used: ${war.opponent.attacks || 0}/${war.teamSize * 2}</p>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-3">
                                <p class="mb-1"><strong>War State:</strong> ${formatUtils.formatWarState(war.state)}</p>
                                ${war.startTime ? `<p class="mb-1"><strong>Start Time:</strong> ${formatUtils.formatDate(war.startTime)}</p>` : ''}
                                ${war.endTime ? `<p class="mb-1"><strong>End Time:</strong> ${formatUtils.formatDate(war.endTime)}</p>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function renderCWLData(cwl) {
        if (!cwl || cwl.state === 'notInWar') return '';

        const clansHtml = cwl.clans?.map(clan => `
            <tr>
                <td>${clan.name}</td>
                <td>${clan.tag}</td>
                <td>${clan.clanLevel}</td>
                <td>${clan.members}</td>
            </tr>
        `).join('') || '';

        return `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card cwl-card">
                        <div class="card-header bg-info text-white">
                            <h5 class="mb-0"><i class="fas fa-crown"></i> Clan War League</h5>
                        </div>
                        <div class="card-body">
                            <div class="cwl-stats">
                                <div class="row">
                                    <div class="col-md-6">
                                        <p><strong>Season:</strong> ${cwl.season}</p>
                                        <p><strong>State:</strong> ${cwl.state}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <p><strong>Clans in Group:</strong> ${cwl.clans?.length || 0}</p>
                                    </div>
                                </div>
                            </div>
                            ${cwl.clans && cwl.clans.length > 0 ? `
                            <h6 class="mt-3">CWL Group Clans</h6>
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Clan</th>
                                            <th>Tag</th>
                                            <th>Level</th>
                                            <th>Members</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${clansHtml}
                                    </tbody>
                                </table>
                            </div>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
});

// Table sorting function
function sortTable(header, columnIndex) {
    const table = header.closest('table');
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
    
    // Show toast notification
    showToast('Table sorted successfully', 'success');
}

// Toast notification function
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