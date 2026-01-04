// Beautiful autocomplete functionality for team/player selection

document.addEventListener('DOMContentLoaded', function() {
    const autocompleteInputs = document.querySelectorAll('.autocomplete-input');
    
    autocompleteInputs.forEach(input => {
        const sport = input.dataset.sport;
        const dropdown = document.getElementById(`dropdown_${sport}`);
        let selectedIndex = -1;
        let suggestions = [];
        let debounceTimer;
        
        // Handle input
        input.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            
            clearTimeout(debounceTimer);
            
            // Show all options if input is empty, filtered if there's a query
            debounceTimer = setTimeout(() => {
                fetchSuggestions(sport, query);
            }, 200);
        });
        
        // Show all options when input is focused and empty
        input.addEventListener('focus', function() {
            if (input.value.trim().length === 0) {
                fetchSuggestions(sport, '');
            }
        });
        
        // Handle keyboard navigation
        input.addEventListener('keydown', function(e) {
            if (!dropdown.classList.contains('show')) return;
            
            const items = dropdown.querySelectorAll('.dropdown-item');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
                updateSelection(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                updateSelection(items);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (selectedIndex >= 0 && items[selectedIndex]) {
                    selectItem(items[selectedIndex]);
                }
            } else if (e.key === 'Escape') {
                dropdown.classList.remove('show');
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!input.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
        
        // Fetch suggestions from API
        function fetchSuggestions(sport, query) {
            fetch(`/api/suggestions/${sport}?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    suggestions = data.suggestions || [];
                    displaySuggestions(suggestions, dropdown, input);
                })
                .catch(error => {
                    console.error('Error fetching suggestions:', error);
                    dropdown.classList.remove('show');
                });
        }
        
        // Display suggestions
        function displaySuggestions(suggestions, dropdown, input) {
            if (suggestions.length === 0) {
                dropdown.classList.remove('show');
                return;
            }
            
            dropdown.innerHTML = '';
            selectedIndex = -1;
            
            // Show all suggestions (no limit)
            suggestions.forEach((suggestion, index) => {
                const item = document.createElement('div');
                item.className = 'dropdown-item';
                item.textContent = suggestion;
                item.dataset.index = index;
                
                item.addEventListener('click', function() {
                    selectItem(item);
                });
                
                item.addEventListener('mouseenter', function() {
                    selectedIndex = index;
                    updateSelection(dropdown.querySelectorAll('.dropdown-item'));
                });
                
                dropdown.appendChild(item);
            });
            
            // Add a count indicator if there are many results
            if (suggestions.length > 20) {
                const countItem = document.createElement('div');
                countItem.className = 'dropdown-count';
                countItem.textContent = `${suggestions.length} options available`;
                dropdown.appendChild(countItem);
            }
            
            dropdown.classList.add('show');
        }
        
        // Update selected item styling
        function updateSelection(items) {
            items.forEach((item, index) => {
                if (index === selectedIndex) {
                    item.classList.add('selected');
                    item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
                } else {
                    item.classList.remove('selected');
                }
            });
        }
        
        // Select an item
        function selectItem(item) {
            input.value = item.textContent;
            dropdown.classList.remove('show');
            input.focus();
            
            // Add a nice animation
            input.style.transform = 'scale(1.02)';
            setTimeout(() => {
                input.style.transform = 'scale(1)';
            }, 200);
        }
    });
});

