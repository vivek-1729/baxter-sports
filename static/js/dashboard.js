// Clean Dashboard - Modal-Based Details

(function() {
    'use strict';
    
    // State management
    let selectedCard = null;
    let heroBackground = null;
    let heroContent = null;
    let cards = [];
    let modalData = {};
    
    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        heroBackground = document.getElementById('heroBackground');
        heroContent = document.getElementById('heroContent');
        // Get cards from both rows
        const firstRowCards = Array.from(document.querySelectorAll('#cardsRailFirst .small-card'));
        const secondRowCards = Array.from(document.querySelectorAll('#cardsRailSecond .small-card'));
        cards = [...firstRowCards, ...secondRowCards];
        
            // Get modal data from template (if available)
        const modalDataScript = document.getElementById('modalDataScript');
        if (modalDataScript) {
            try {
                modalData = JSON.parse(modalDataScript.textContent);
            } catch (e) {
                console.error('Error parsing modal data:', e);
            }
        }
        
        // Get events data for async image loading
        let eventsData = [];
        const eventsDataScript = document.getElementById('eventsData');
        if (eventsDataScript) {
            try {
                eventsData = JSON.parse(eventsDataScript.textContent);
            } catch (e) {
                console.error('Error parsing events data:', e);
            }
        }
        
        // Set first card as selected by default
        const firstCard = document.querySelector('.small-card[data-selected="true"]');
        if (firstCard) {
            // Set initial background image immediately
            const initialImage = firstCard.getAttribute('data-background-image');
            if (initialImage && heroBackground) {
                heroBackground.style.backgroundImage = `url(${initialImage})`;
                heroBackground.classList.add('has-image');
                heroBackground.style.opacity = '1';
            }
            selectCard(firstCard);
            
            // Force update hero content to apply completed game layout if needed
            // This ensures the initial card shows the proper score display
            setTimeout(() => {
                updateHeroContent(firstCard);
            }, 100);
        }
        
        // Add click handlers to all cards
        cards.forEach(card => {
            card.addEventListener('click', function() {
                selectCard(card);
            });
        });
        
        // Load images asynchronously for cards that don't have images yet
        // Delay slightly to ensure page is fully rendered
        setTimeout(() => {
            loadImagesAsync();
        }, 500);
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                navigateCards(e.key === 'ArrowRight' ? 1 : -1);
            } else if (e.key === 'Escape') {
                closeModal();
            }
        });
        
        // Navbar sport buttons
        const sportButtons = document.querySelectorAll('.navbar-sport-btn');
        sportButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const sport = this.getAttribute('data-sport');
                filterBySport(sport);
                
                // Update active state
                sportButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });
        
        // Quick info card clicks (open modals)
        const quickInfoCards = document.querySelectorAll('.quick-info-card');
        quickInfoCards.forEach(card => {
            card.addEventListener('click', function() {
                const modalType = this.getAttribute('data-modal');
                openModal(modalType);
            });
        });
        
        // Modal close button
        const modalClose = document.getElementById('modalClose');
        const modalOverlay = document.getElementById('modalOverlay');
        if (modalClose) {
            modalClose.addEventListener('click', closeModal);
        }
        if (modalOverlay) {
            modalOverlay.addEventListener('click', function(e) {
                if (e.target === modalOverlay) {
                    closeModal();
                }
            });
        }
        
    });
    
    /**
     * Select a card and update hero section
     */
    function selectCard(card) {
        // Remove previous selection
        if (selectedCard) {
            selectedCard.removeAttribute('data-selected');
        }
        
        // Set new selection
        selectedCard = card;
        card.setAttribute('data-selected', 'true');
        
        // Update hero background image
        updateHeroBackground(card);
        
        // Update hero content
        updateHeroContent(card);
        
        // Scroll card into view smoothly
        card.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
            inline: 'center'
        });
    }
    
    /**
     * Update hero background image
     */
    function updateHeroBackground(card) {
        if (!heroBackground) return;
        
        const imageUrl = card.getAttribute('data-background-image');
        
        if (imageUrl) {
            // Create new image element for smooth transition
            const newImg = new Image();
            newImg.onload = function() {
                // Fade out current
                heroBackground.style.opacity = '0';
                
                setTimeout(() => {
                    // Update background
                    heroBackground.style.backgroundImage = `url(${imageUrl})`;
                    heroBackground.classList.add('has-image');
                    
                    // Fade in new
                    setTimeout(() => {
                        heroBackground.style.opacity = '1';
                    }, 50);
                }, 300);
            };
            newImg.src = imageUrl;
        } else {
            // Fade out if no image
            heroBackground.style.opacity = '0';
            heroBackground.classList.remove('has-image');
        }
    }
    
    /**
     * Update hero content with new comprehensive layout
     */
    function updateHeroContent(card) {
        if (!heroContent) return;
        
        // Get data from card
        const sportLabel = card.querySelector('.card-sport-label')?.textContent || '';
        const teams = card.querySelectorAll('.card-team');
        const isLive = card.querySelector('.card-live-badge');
        const eventId = card.getAttribute('data-event-id');
        
        // Get event data
        let isCompleted = false;
        let eventData = null;
        const eventsDataScript = document.getElementById('eventsData');
        if (eventsDataScript && eventId) {
            try {
                const allEvents = JSON.parse(eventsDataScript.textContent || eventsDataScript.innerHTML);
                eventData = allEvents.find(e => e.fixture?.id?.toString() === eventId.toString());
                isCompleted = eventData?.is_completed || false;
            } catch (e) {
                console.error('Error parsing events data:', e);
            }
        }
        
        if (!eventData || teams.length < 2) return;
        
        const homeTeam = teams[0].textContent;
        const awayTeam = teams[1].textContent;
        
        // Update title
        const heroTitle = document.getElementById('heroTitle');
        if (heroTitle) {
            heroTitle.textContent = `${homeTeam} vs ${awayTeam}`;
        }
        
        // Update badges
        updateHeroBadges(sportLabel, isLive, isCompleted);
        
        // Fetch and update hero data (includes stats for team info row)
        updateHeroData(card);
    }
    
    /**
     * Fetch and update hero data (stats, news, standings) for the selected event
     */
    function updateHeroData(card) {
        // Get event ID from card
        const eventId = card.getAttribute('data-event-id');
        if (!eventId) {
            console.log('No event ID found on card');
            return;
        }
        
        // Get events data
        const eventsDataScript = document.getElementById('eventsData');
        if (!eventsDataScript) {
            console.log('Events data script not found');
            return;
        }
        
        let eventsData = [];
        try {
            const scriptContent = eventsDataScript.textContent || eventsDataScript.innerHTML;
            eventsData = JSON.parse(scriptContent);
        } catch (e) {
            console.error('Error parsing events data:', e);
            return;
        }
        
        // Find the event
        const event = eventsData.find(e => e.fixture?.id?.toString() === eventId.toString());
        if (!event) {
            console.log('Event not found for ID:', eventId);
            return;
        }
        
        // Fetch hero data from API
        fetch('/api/hero-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ event: event })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(heroData => {
            // Update modal data so "View All" shows correct data
            modalData = {
                stats: heroData.stats || modalData.stats,
                standings: heroData.standings || modalData.standings,
                news: heroData.news || modalData.news
            };
            
            // Update ALL hero elements with new comprehensive layout
            updateAllHeroElements(heroData, event);
        })
        .catch(error => {
            console.error('Error loading hero data:', error);
        });
    }
    
    /**
     * Update all hero elements with new comprehensive data
     */
    function updateAllHeroElements(heroData, event) {
        // Update team info row with records and standings
        updateTeamInfo(heroData, event.sport_key);
        
        // Update game-specific sections (score/game info/content boxes)
        updateGameSpecificSections(heroData, event);
    }
    
    /**
     * Update team info row with records and standings
     */
    function updateTeamInfo(heroData, sportKey) {
        const teamInfoRow = document.getElementById('heroTeamInfo');
        if (!teamInfoRow) return;
        
        const teamBlocks = teamInfoRow.querySelectorAll('.hero-team-block');
        if (teamBlocks.length >= 2) {
            // Update home team (first block)
            if (heroData.home_team_stats && teamBlocks[0]) {
                const statsDiv = teamBlocks[0].querySelector('.hero-team-stats');
                if (statsDiv) {
                    const stats = heroData.home_team_stats;
                    statsDiv.innerHTML = `
                        <div class="hero-team-stat">
                            <span>${stats.wins}-${stats.losses}</span>
                            <span class="hero-stat-icon" onclick="showStandingsModal('${sportKey}')">📊</span>
                        </div>
                        <div class="hero-team-stat">
                            <span>#${stats.rank} in ${stats.division}</span>
                            <span class="hero-stat-icon" onclick="showStandingsModal('${sportKey}')">📈</span>
                        </div>
                    `;
                }
            }
            
            // Update away team (second block)
            if (heroData.away_team_stats && teamBlocks[1]) {
                const statsDiv = teamBlocks[1].querySelector('.hero-team-stats');
                if (statsDiv) {
                    const stats = heroData.away_team_stats;
                    statsDiv.innerHTML = `
                        <div class="hero-team-stat">
                            <span>${stats.wins}-${stats.losses}</span>
                            <span class="hero-stat-icon" onclick="showStandingsModal('${sportKey}')">📊</span>
                        </div>
                        <div class="hero-team-stat">
                            <span>#${stats.rank} in ${stats.division}</span>
                            <span class="hero-stat-icon" onclick="showStandingsModal('${sportKey}')">📈</span>
                        </div>
                    `;
                }
            }
        }
    }
    
    /**
     * Update game-specific sections based on game status
     */
    function updateGameSpecificSections(heroData, event) {
        const isCompleted = event.is_completed || false;
        
        // Check if elements exist
        const heroScore = document.getElementById('heroScore');
        const heroGameInfo = document.getElementById('heroGameInfo');
        const heroContentBoxes = document.getElementById('heroContentBoxes');
        const heroMeta = document.getElementById('heroMeta');
        
        if (isCompleted) {
            // Update score display
            if (heroScore) {
                const homeScore = event.goals?.home || 0;
                const awayScore = event.goals?.away || 0;
                heroScore.innerHTML = `
                    <span class="hero-score-number ${homeScore > awayScore ? 'winner' : ''}">${homeScore}</span>
                    <span class="hero-score-separator">-</span>
                    <span class="hero-score-number ${awayScore > homeScore ? 'winner' : ''}">${awayScore}</span>
                `;
            }
            
            // Update content boxes with recap and highlights
            if (heroContentBoxes) {
                heroContentBoxes.innerHTML = `
                    <div class="hero-content-box">
                        <div class="hero-box-header" onclick="toggleContentBox(this)">
                            <div class="hero-box-header-left">
                                <span class="hero-box-icon">📝</span>
                                <span class="hero-box-title">Game Recap</span>
                            </div>
                            <span class="hero-box-expand-icon">▼</span>
                        </div>
                        <div class="hero-box-content">
                            ${heroData.recap || 'Game recap coming soon...'}
                        </div>
                    </div>
                    <div class="hero-content-box">
                        <div class="hero-box-header" onclick="toggleContentBox(this)">
                            <div class="hero-box-header-left">
                                <span class="hero-box-icon">🎬</span>
                                <span class="hero-box-title">Highlights</span>
                            </div>
                            <span class="hero-box-expand-icon">▼</span>
                        </div>
                        <div class="hero-box-content">
                            <div class="hero-highlights-list">
                                ${(heroData.highlights || []).map(h => `
                                    <div class="hero-highlight-item">
                                        <span class="hero-highlight-title">${h.title}</span>
                                        <span class="hero-highlight-duration">${h.duration}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `;
            }
        } else {
            // Update game info bar
            if (heroGameInfo) {
                const formattedDate = formatGameDate(event.fixture?.date);
                heroGameInfo.innerHTML = `
                    <div class="hero-info-item">
                        <span class="hero-info-icon">📅</span>
                        <span>${formattedDate}</span>
                    </div>
                    <span class="hero-info-divider">|</span>
                    <div class="hero-info-item">
                        <span class="hero-info-icon">🕐</span>
                        <span>${heroData.game_time || '7:30 PM PST'}</span>
                    </div>
                    <span class="hero-info-divider">|</span>
                    <div class="hero-info-item">
                        <span class="hero-info-icon">📺</span>
                        <span>${heroData.network || 'ESPN'}</span>
                    </div>
                `;
            }
            
            // Update content boxes with preview and team news
            if (heroContentBoxes) {
                heroContentBoxes.innerHTML = `
                    <div class="hero-content-box">
                        <div class="hero-box-header" onclick="toggleContentBox(this)">
                            <div class="hero-box-header-left">
                                <span class="hero-box-icon">📰</span>
                                <span class="hero-box-title">Game Preview</span>
                            </div>
                            <span class="hero-box-expand-icon">▼</span>
                        </div>
                        <div class="hero-box-content">
                            ${heroData.preview || 'Game preview coming soon...'}
                        </div>
                    </div>
                    <div class="hero-content-box">
                        <div class="hero-box-header" onclick="toggleContentBox(this)">
                            <div class="hero-box-header-left">
                                <span class="hero-box-icon">📰</span>
                                <span class="hero-box-title">Team News</span>
                            </div>
                            <span class="hero-box-expand-icon">▼</span>
                        </div>
                        <div class="hero-box-content">
                            ${heroData.team_news || 'No recent news available.'}
                        </div>
                    </div>
                `;
            }
        }
    }
    
    /**
     * Update quick info cards with new hero data
     */
    function updateQuickInfoCards(heroData) {
        const quickInfoCards = document.querySelector('.quick-info-cards');
        if (!quickInfoCards) return;
        
        // Update or create stats card
        if (heroData.stats) {
            let statsCard = quickInfoCards.querySelector('[data-modal="stats"]');
            if (!statsCard) {
                statsCard = createQuickInfoCard('stats', 'Stats');
                quickInfoCards.appendChild(statsCard);
            }
            fadeUpdateCard(statsCard, () => updateStatsCard(statsCard, heroData.stats));
        }
        
        // Update or create standings card
        if (heroData.standings) {
            let standingsCard = quickInfoCards.querySelector('[data-modal="standings"]');
            if (!standingsCard) {
                standingsCard = createQuickInfoCard('standings', 'Standings');
                quickInfoCards.appendChild(standingsCard);
            }
            fadeUpdateCard(standingsCard, () => updateStandingsCard(standingsCard, heroData.standings));
        }
        
        // Update or create news card
        if (heroData.news) {
            let newsCard = quickInfoCards.querySelector('[data-modal="news"]');
            if (!newsCard) {
                newsCard = createQuickInfoCard('news', 'News');
                quickInfoCards.appendChild(newsCard);
            }
            fadeUpdateCard(newsCard, () => updateNewsCard(newsCard, heroData.news));
        }
    }
    
    /**
     * Fade out, update, then fade in a card
     */
    function fadeUpdateCard(card, updateFunction) {
        const content = card.querySelector('.quick-info-content');
        if (!content) {
            updateFunction();
            return;
        }
        
        // Fade out
        content.style.opacity = '0';
        content.style.transition = 'opacity 0.2s';
        
        setTimeout(() => {
            // Update content
            updateFunction();
            
            // Fade in
            setTimeout(() => {
                content.style.opacity = '1';
            }, 10);
        }, 200);
    }
    
    /**
     * Create a quick info card structure
     */
    function createQuickInfoCard(modalType, title) {
        const card = document.createElement('div');
        card.className = 'quick-info-card';
        card.setAttribute('data-modal', modalType);
        
        const header = document.createElement('div');
        header.className = 'quick-info-header';
        
        const titleEl = document.createElement('h3');
        titleEl.className = 'quick-info-title';
        titleEl.textContent = title;
        
        const more = document.createElement('span');
        more.className = 'quick-info-more';
        more.textContent = 'View All →';
        
        header.appendChild(titleEl);
        header.appendChild(more);
        
        const content = document.createElement('div');
        content.className = 'quick-info-content';
        
        card.appendChild(header);
        card.appendChild(content);
        
        // Add click handler for modal
        card.addEventListener('click', function() {
            openModal(modalType);
        });
        
        return card;
    }
    
    /**
     * Update stats card content
     */
    function updateStatsCard(card, stats) {
        const content = card.querySelector('.quick-info-content');
        if (!content) return;
        
        content.innerHTML = `
            <div class="quick-stat">
                <div class="quick-stat-value">${stats.wins}-${stats.losses}</div>
                <div class="quick-stat-label">Record</div>
            </div>
            <div class="quick-stat">
                <div class="quick-stat-value">${(stats.win_percentage * 100).toFixed(1)}%</div>
                <div class="quick-stat-label">Win %</div>
            </div>
            <div class="quick-stat">
                <div class="quick-stat-value">#${stats.rank}</div>
                <div class="quick-stat-label">Rank</div>
            </div>
        `;
    }
    
    /**
     * Update standings card content
     */
    function updateStandingsCard(card, standings) {
        const content = card.querySelector('.quick-info-content');
        if (!content) return;
        
        let html = '';
        if (standings && standings.length > 0) {
            const standingGroup = standings[0];
            if (standingGroup.league && standingGroup.league.standings) {
                for (const group of standingGroup.league.standings) {
                    for (const team of group.slice(0, 3)) {
                        html += `
                            <div class="quick-standing-item">
                                <span class="quick-standing-rank">#${team.rank}</span>
                                <span class="quick-standing-team">${team.team.name}</span>
                            </div>
                        `;
                    }
                }
            }
        }
        
        content.innerHTML = html || '<div class="quick-standing-item">No standings available</div>';
    }
    
    /**
     * Update news card content
     */
    function updateNewsCard(card, news) {
        const content = card.querySelector('.quick-info-content');
        if (!content) return;
        
        let html = '';
        if (news && news.length > 0) {
            for (const article of news.slice(0, 2)) {
                html += `
                    <div class="quick-news-item">
                        <div class="quick-news-title">${article.title}</div>
                        <div class="quick-news-date">${article.date}</div>
                    </div>
                `;
            }
        }
        
        content.innerHTML = html || '<div class="quick-news-item">No news available</div>';
    }
    
    /**
     * Update hero badges
     */
    function updateHeroBadges(sportLabel, isLive, isCompleted = false) {
        const heroMain = heroContent.querySelector('.hero-main');
        if (!heroMain) return;
        
        // Remove existing badges
        const existingBadges = heroMain.querySelectorAll('.hero-badge, .hero-live-badge, .hero-final-badge');
        existingBadges.forEach(badge => badge.remove());
        
        // Find or create badges container
        let badgesContainer = heroMain.querySelector('.hero-badges');
        if (!badgesContainer) {
            badgesContainer = document.createElement('div');
            badgesContainer.className = 'hero-badges';
            heroMain.insertBefore(badgesContainer, heroMain.firstChild);
        }
        
        // Add sport badge
        if (sportLabel) {
            const badge = document.createElement('div');
            badge.className = 'hero-badge';
            badge.textContent = sportLabel;
            badgesContainer.appendChild(badge);
        }
        
        // Add FINAL badge for completed games
        if (isCompleted) {
            const finalBadge = document.createElement('div');
            finalBadge.className = 'hero-final-badge';
            finalBadge.textContent = 'FINAL';
            badgesContainer.appendChild(finalBadge);
        }
        // Add live badge if needed (only if not completed)
        else if (isLive) {
            const liveBadge = document.createElement('div');
            liveBadge.className = 'hero-live-badge';
            liveBadge.textContent = 'LIVE';
            badgesContainer.appendChild(liveBadge);
        }
    }
    
    /**
     * Navigate to adjacent card
     */
    function navigateCards(direction) {
        if (!selectedCard || cards.length === 0) return;
        
        const currentIndex = cards.indexOf(selectedCard);
        const nextIndex = currentIndex + direction;
        
        if (nextIndex >= 0 && nextIndex < cards.length) {
            selectCard(cards[nextIndex]);
        }
    }
    
    /**
     * Filter cards by sport
     */
    function filterBySport(sport) {
        cards.forEach(card => {
            const cardSport = card.getAttribute('data-sport');
            if (cardSport === sport) {
                card.style.display = 'flex';
                // Select first visible card
                if (!selectedCard || selectedCard.style.display === 'none') {
                    selectCard(card);
                }
            } else {
                card.style.display = 'none';
            }
        });
        
        // Show all if no filter
        if (!sport) {
            cards.forEach(card => {
                card.style.display = 'flex';
            });
        }
    }
    
    /**
     * Open modal with content
     */
    function openModal(type) {
        const modalOverlay = document.getElementById('modalOverlay');
        const modalContent = document.getElementById('modalContent');
        
        if (!modalOverlay || !modalContent) return;
        
        let content = '';
        
        switch(type) {
            case 'news':
                content = generateNewsModal();
                break;
            case 'standings':
                content = generateStandingsModal();
                break;
            case 'stats':
                content = generateStatsModal();
                break;
        }
        
        modalContent.innerHTML = content;
        modalOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    /**
     * Close modal
     */
    function closeModal() {
        const modalOverlay = document.getElementById('modalOverlay');
        if (modalOverlay) {
            modalOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    /**
     * Generate news modal content
     */
    function generateNewsModal() {
        const news = modalData.news || [];
        if (news.length === 0) {
            return '<h2>News</h2><p>No news available at this time.</p>';
        }
        
        let html = '<h2>Latest News</h2><div class="modal-news-list">';
        news.forEach(article => {
            html += `
                <div class="modal-news-item">
                    <h3 class="modal-news-title">${article.title}</h3>
                    <p class="modal-news-summary">${article.summary || ''}</p>
                    <div class="modal-news-meta">${article.date} · ${article.source}</div>
                </div>
            `;
        });
        html += '</div>';
        return html;
    }
    
    /**
     * Generate standings modal content
     */
    function generateStandingsModal() {
        const standings = modalData.standings || [];
        if (standings.length === 0) {
            return '<h2>Standings</h2><p>No standings available at this time.</p>';
        }
        
        let html = '<h2>League Standings</h2><div class="modal-standings-table">';
        standings.forEach(standingGroup => {
            if (standingGroup.league && standingGroup.league.standings) {
                standingGroup.league.standings.forEach(group => {
                    group.forEach(team => {
                        html += `
                            <div class="modal-standing-row">
                                <span class="modal-standing-rank">#${team.rank}</span>
                                <span class="modal-standing-team">${team.team.name}</span>
                                <span class="modal-standing-points">${team.points} pts</span>
                            </div>
                        `;
                    });
                });
            }
        });
        html += '</div>';
        return html;
    }
    
    /**
     * Generate stats modal content
     */
    function generateStatsModal() {
        const stats = modalData.stats || {};
        if (Object.keys(stats).length === 0) {
            return '<h2>Statistics</h2><p>No statistics available at this time.</p>';
        }
        
        let html = '<h2>Team Statistics</h2><div class="modal-stats-grid">';
        html += `
            <div class="modal-stat-item">
                <div class="modal-stat-label">Record</div>
                <div class="modal-stat-value">${stats.wins}-${stats.losses}</div>
            </div>
            <div class="modal-stat-item">
                <div class="modal-stat-label">Win Percentage</div>
                <div class="modal-stat-value">${(stats.win_percentage * 100).toFixed(1)}%</div>
            </div>
            <div class="modal-stat-item">
                <div class="modal-stat-label">Rank</div>
                <div class="modal-stat-value">#${stats.rank}</div>
            </div>
            <div class="modal-stat-item">
                <div class="modal-stat-label">Points Per Game</div>
                <div class="modal-stat-value">${stats.points_per_game || 'N/A'}</div>
            </div>
        `;
        html += '</div>';
        return html;
    }
    
    // Expose for potential external use
    window.dashboardController = {
        selectCard: selectCard,
        navigateCards: navigateCards,
        openModal: openModal,
        closeModal: closeModal
    };
    // Async image loading function
    function loadImagesAsync() {
        console.log('loadImagesAsync called');
        
        // Find all cards without images
        const cardsWithoutImages = cards.filter(card => {
            const currentImage = card.getAttribute('data-background-image');
            return !currentImage || currentImage === '';
        });
        
        console.log(`Found ${cardsWithoutImages.length} cards without images`);
        
        if (cardsWithoutImages.length === 0) {
            console.log('All images already loaded');
            return; // All images already loaded
        }
        
        // Get events data
        const eventsDataScript = document.getElementById('eventsData');
        if (!eventsDataScript) {
            console.log('Events data script not found');
            return;
        }
        
        let eventsData = [];
        try {
            // Get the text content and parse it
            const scriptContent = eventsDataScript.textContent || eventsDataScript.innerHTML;
            eventsData = JSON.parse(scriptContent);
            console.log('Events data loaded:', eventsData.length, 'events');
        } catch (e) {
            console.error('Error parsing events data:', e);
            return;
        }
        
        // Create a map of event IDs to events
        const eventMap = {};
        eventsData.forEach(event => {
            const eventId = event.fixture?.id;
            if (eventId) {
                eventMap[eventId] = event;
            }
        });
        
        console.log('Event map created with', Object.keys(eventMap).length, 'events');
        
        // Load images for cards without images (with delay to avoid overwhelming)
        cardsWithoutImages.forEach((card, index) => {
            const eventId = card.getAttribute('data-event-id');
            const event = eventMap[eventId];
            
            if (!event) {
                console.log('Event not found for card:', eventId);
                return;
            }
            
            // Stagger requests to avoid rate limiting
            setTimeout(() => {
                console.log(`Loading image for event ${eventId} (${index + 1}/${cardsWithoutImages.length})`);
                
                fetch('/api/resolve-image', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ event: event })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.image_url) {
                        console.log(`Image resolved for event ${eventId}:`, data.image_url);
                        
                        // Update the card's data attribute
                        card.setAttribute('data-background-image', data.image_url);
                        
                        // Get the image container
                        const imageContainer = card.querySelector('.small-card-image');
                        if (!imageContainer) {
                            console.log('Image container not found for card');
                            return;
                        }
                        
                        // Check if there's already an img tag or placeholder
                        const existingImg = imageContainer.querySelector('img');
                        const placeholder = imageContainer.querySelector('.card-placeholder');
                        
                        if (existingImg) {
                            // Update existing img
                            const img = new Image();
                            img.onload = function() {
                                existingImg.src = data.image_url;
                                existingImg.style.opacity = '0';
                                existingImg.style.transition = 'opacity 0.3s';
                                setTimeout(() => {
                                    existingImg.style.opacity = '1';
                                }, 10);
                            };
                            img.onerror = function() {
                                console.error('Failed to load image:', data.image_url);
                            };
                            img.src = data.image_url;
                        } else if (placeholder) {
                            // Replace placeholder with img tag
                            const img = document.createElement('img');
                            img.src = data.image_url;
                            img.alt = 'Event image';
                            img.loading = 'lazy';
                            img.style.opacity = '0';
                            img.style.transition = 'opacity 0.3s';
                            
                            img.onload = function() {
                                placeholder.remove();
                                imageContainer.appendChild(img);
                                setTimeout(() => {
                                    img.style.opacity = '1';
                                }, 10);
                                console.log(`Image inserted for event ${eventId}`);
                            };
                            
                            img.onerror = function() {
                                console.error('Failed to load image:', data.image_url);
                            };
                        } else {
                            console.log('No existing img or placeholder found');
                        }
                        
                        // If this is the selected card, update hero background
                        if (card === selectedCard) {
                            updateHeroBackground(data.image_url);
                        }
                    } else {
                        console.log(`No image URL returned for event ${eventId}`);
                    }
                })
                .catch(error => {
                    console.error('Error loading image for event', eventId, ':', error);
                });
            }, index * 200); // 200ms delay between each request
        });
    }
    
    /**
     * Format game date - show day name if within a week, otherwise "Month Day" format
     */
    function formatGameDate(dateString) {
        if (!dateString) return '';
        
        const gameDate = new Date(dateString);
        const now = new Date();
        const oneWeek = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds
        const diff = gameDate.getTime() - now.getTime();
        
        if (Math.abs(diff) <= oneWeek) {
            // Within a week - show day name
            const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            return days[gameDate.getDay()];
        } else {
            // Beyond a week - show "Month Day" format
            const months = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December'];
            return `${months[gameDate.getMonth()]} ${gameDate.getDate()}`;
        }
    }
    
    // Make formatGameDate available in the outer scope
    window.formatGameDate = formatGameDate;

})();

// Global helper functions for onclick handlers

/**
 * Toggle content box expand/collapse
 */
function toggleContentBox(headerElement) {
    const contentBox = headerElement.closest('.hero-content-box');
    const content = contentBox.querySelector('.hero-box-content');
    const expandIcon = headerElement.querySelector('.hero-box-expand-icon');
    
    content.classList.toggle('collapsed');
    expandIcon.classList.toggle('expanded');
}

/**
 * Show standings modal for a sport
 */
function showStandingsModal(sportKey) {
    const modal = document.getElementById('standingsModal');
    const title = document.getElementById('standingsModalTitle');
    const divisionsContainer = document.getElementById('standingsDivisions');
    
    if (!modal || !title || !divisionsContainer) return;
    
    // Set title
    title.textContent = `${sportKey.toUpperCase()} Standings`;
    
    // Fetch standings data
    fetch('/api/standings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ sport_key: sportKey })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            divisionsContainer.innerHTML = '<p style="text-align: center; padding: 20px;">Failed to load standings.</p>';
            return;
        }
        
        // Group teams by division
        const divisions = {};
        if (data.league && data.league.standings && data.league.standings.length > 0) {
            data.league.standings[0].forEach(team => {
                const divisionName = team.division || 'Conference';
                if (!divisions[divisionName]) {
                    divisions[divisionName] = [];
                }
                divisions[divisionName].push(team);
            });
        }
        
        // Render divisions
        let html = '';
        for (const [divisionName, teams] of Object.entries(divisions)) {
            html += `
                <div class="standings-division">
                    <h3 class="standings-division-title">${divisionName}</h3>
                    <table class="standings-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Team</th>
                                <th>W</th>
                                <th>L</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${teams.map(team => `
                                <tr>
                                    <td class="standings-rank">${team.rank}</td>
                                    <td>
                                        <div class="standings-team">
                                            ${team.team.logo ? `<img src="${team.team.logo}" alt="${team.team.name}" class="standings-team-logo">` : ''}
                                            <span>${team.team.name}</span>
                                        </div>
                                    </td>
                                    <td class="standings-record">${team.wins}</td>
                                    <td class="standings-record">${team.losses}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }
        
        divisionsContainer.innerHTML = html || '<p style="text-align: center; padding: 20px;">No standings data available.</p>';
        
        // Show modal
        modal.classList.add('active');
    })
    .catch(error => {
        console.error('Error fetching standings:', error);
        divisionsContainer.innerHTML = '<p style="text-align: center; padding: 20px;">Failed to load standings.</p>';
        modal.classList.add('active');
    });
}

/**
 * Close standings modal
 */
function closeStandingsModal() {
    const modal = document.getElementById('standingsModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    const modal = document.getElementById('standingsModal');
    if (modal && e.target === modal) {
        closeStandingsModal();
    }
});
