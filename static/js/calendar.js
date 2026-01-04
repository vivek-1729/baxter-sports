// Calendar functionality

let currentDate = new Date();
let currentMonth = currentDate.getMonth();
let currentYear = currentDate.getFullYear();

const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
];

const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

// Initialize calendar
document.addEventListener('DOMContentLoaded', function() {
    renderCalendar();
    
    // Month navigation
    document.getElementById('prevMonth').addEventListener('click', () => {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        renderCalendar();
    });
    
    document.getElementById('nextMonth').addEventListener('click', () => {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        renderCalendar();
    });
    
    // Filter checkboxes
    document.querySelectorAll('.sport-filter').forEach(checkbox => {
        checkbox.addEventListener('change', renderCalendar);
    });
});

function renderCalendar() {
    const monthYear = document.getElementById('monthYear');
    monthYear.textContent = `${monthNames[currentMonth]} ${currentYear}`;
    
    const calendarGrid = document.getElementById('calendarGrid');
    calendarGrid.innerHTML = '';
    
    // Add day headers
    dayNames.forEach(day => {
        const header = document.createElement('div');
        header.className = 'calendar-day-header';
        header.textContent = day;
        calendarGrid.appendChild(header);
    });
    
    // Get first day of month and number of days
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    const daysInPrevMonth = new Date(currentYear, currentMonth, 0).getDate();
    
    // Get active filters
    const activeSports = Array.from(document.querySelectorAll('.sport-filter:checked'))
        .map(cb => cb.dataset.sport);
    
    // Previous month days
    for (let i = firstDay - 1; i >= 0; i--) {
        const day = daysInPrevMonth - i;
        const dayElement = createDayElement(day, currentMonth - 1, currentYear, true, activeSports);
        calendarGrid.appendChild(dayElement);
    }
    
    // Current month days
    for (let day = 1; day <= daysInMonth; day++) {
        const dayElement = createDayElement(day, currentMonth, currentYear, false, activeSports);
        calendarGrid.appendChild(dayElement);
    }
    
    // Next month days (to fill the grid)
    const totalCells = calendarGrid.children.length - 7; // Subtract headers
    const remainingCells = 42 - totalCells; // 6 rows * 7 days = 42
    for (let day = 1; day <= remainingCells; day++) {
        const dayElement = createDayElement(day, currentMonth + 1, currentYear, true, activeSports);
        calendarGrid.appendChild(dayElement);
    }
}

function createDayElement(day, month, year, isOtherMonth, activeSports) {
    const dayElement = document.createElement('div');
    dayElement.className = 'calendar-day';
    if (isOtherMonth) {
        dayElement.classList.add('other-month');
    }
    
    // Check if today
    const today = new Date();
    if (!isOtherMonth && day === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
        dayElement.classList.add('today');
    }
    
    // Day number
    const dayNumber = document.createElement('div');
    dayNumber.className = 'calendar-day-number';
    dayNumber.textContent = day;
    dayElement.appendChild(dayNumber);
    
    // Games container
    const gamesContainer = document.createElement('div');
    gamesContainer.className = 'calendar-day-games';
    
    // Find games for this date
    const dateStr = formatDate(year, month, day);
    const games = getGamesForDate(dateStr, activeSports);
    
    games.forEach(game => {
        const gameItem = document.createElement('div');
        gameItem.className = 'game-item';
        
        if (game.is_live) {
            gameItem.classList.add('live');
        } else if (game.is_completed) {
            gameItem.classList.add('completed');
        }
        
        const sportIcon = document.createElement('span');
        sportIcon.className = 'game-sport-icon';
        sportIcon.textContent = sports[game.sport_key]?.icon || '🏆';
        
        const gameText = document.createElement('span');
        if (game.teams && game.teams.home && game.teams.away) {
            const homeAbbrev = getAbbrev(game.sport_key, game.teams.home.name);
            const awayAbbrev = getAbbrev(game.sport_key, game.teams.away.name);
            gameText.textContent = `${homeAbbrev} vs ${awayAbbrev}`;
        } else {
            gameText.textContent = game.league?.name || 'Game';
        }
        
        gameItem.appendChild(sportIcon);
        gameItem.appendChild(gameText);
        gamesContainer.appendChild(gameItem);
    });
    
    dayElement.appendChild(gamesContainer);
    return dayElement;
}

function formatDate(year, month, day) {
    // Format as YYYY-MM-DD
    const monthStr = String(month + 1).padStart(2, '0');
    const dayStr = String(day).padStart(2, '0');
    return `${year}-${monthStr}-${dayStr}`;
}

function getGamesForDate(dateStr, activeSports) {
    const games = [];
    
    // Check all sports
    Object.keys(gamesData).forEach(sportKey => {
        if (!activeSports.includes(sportKey)) return;
        
        const sportGames = gamesData[sportKey];
        
        // Check live games
        if (sportGames.live) {
            sportGames.live.forEach(game => {
                const gameDate = game.fixture?.date?.substring(0, 10);
                if (gameDate === dateStr) {
                    games.push({ ...game, sport_key: sportKey, is_live: true });
                }
            });
        }
        
        // Check upcoming games
        if (sportGames.upcoming) {
            sportGames.upcoming.forEach(game => {
                const gameDate = game.fixture?.date?.substring(0, 10);
                if (gameDate === dateStr) {
                    games.push({ ...game, sport_key: sportKey, is_live: false });
                }
            });
        }
        
        // Check recent games
        if (sportGames.recent) {
            sportGames.recent.forEach(game => {
                const gameDate = game.fixture?.date?.substring(0, 10);
                if (gameDate === dateStr) {
                    games.push({ ...game, sport_key: sportKey, is_completed: true });
                }
            });
        }
    });
    
    return games;
}

function getAbbrev(sport, teamName) {
    // Simple abbreviation - take first 3-4 letters
    if (!teamName) return '';
    const words = teamName.split(' ');
    if (words.length > 1) {
        return words.map(w => w[0]).join('').substring(0, 3).toUpperCase();
    }
    return teamName.substring(0, 3).toUpperCase();
}

