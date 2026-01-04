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
        }
        
        // Add click handlers to all cards
        cards.forEach(card => {
            card.addEventListener('click', function() {
                selectCard(card);
            });
        });
        
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
     * Update hero content with card data
     */
    function updateHeroContent(card) {
        if (!heroContent) return;
        
        // Get data from card
        const sportLabel = card.querySelector('.card-sport-label')?.textContent || '';
        const teams = card.querySelectorAll('.card-team');
        const cardMeta = card.querySelector('.card-meta');
        const isLive = card.querySelector('.card-live-badge');
        
        // Update hero title
        const heroTitle = document.getElementById('heroTitle');
        if (heroTitle && teams.length >= 2) {
            heroTitle.textContent = `${teams[0].textContent} vs ${teams[1].textContent}`;
        } else {
            const eventName = card.querySelector('.card-event-name')?.textContent || '';
            if (heroTitle) heroTitle.textContent = eventName;
        }
        
        // Update hero meta
        const heroMeta = document.getElementById('heroMeta');
        if (heroMeta && cardMeta) {
            heroMeta.innerHTML = cardMeta.innerHTML;
        }
        
        // Update hero description (placeholder for now)
        const heroDescription = document.getElementById('heroDescription');
        if (heroDescription) {
            heroDescription.textContent = 'Upcoming sports event';
        }
        
        // Update badges
        updateHeroBadges(sportLabel, isLive);
    }
    
    /**
     * Update hero badges
     */
    function updateHeroBadges(sportLabel, isLive) {
        const heroMain = heroContent.querySelector('.hero-main');
        if (!heroMain) return;
        
        // Remove existing badges
        const existingBadges = heroMain.querySelectorAll('.hero-badge, .hero-live-badge');
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
        
        // Add live badge if needed
        if (isLive) {
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
})();
