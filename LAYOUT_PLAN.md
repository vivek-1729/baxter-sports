# Dashboard Layout Plan

## Design Principles
- **More whitespace** - Better breathing room between elements
- **Less blur** - Reduce backdrop-filter usage, cleaner backgrounds
- **Modal-based details** - Keep hero clean, show details in modals
- **Better spacing** - Generous padding and margins
- **Smaller card images** - More room for text info

## Layout Structure

### 1. Top Navbar
- Simple, clean design
- Minimal blur (subtle background)
- Sport buttons with icons
- Fixed at top

### 2. Hero Section
- Full-screen background image
- Main content: Title, score, venue
- Quick info cards (3 cards side by side):
  - Stats preview (click to open modal)
  - Standings preview (click to open modal)  
  - News preview (1-2 headlines, click to see all)
- More spacing, less clutter

### 3. Cards Section
- Smaller images (reduce height)
- More text info visible
- Better spacing between cards
- Cleaner borders (less blur)

### 4. Modals
- News Modal: All articles, scrollable
- Standings Modal: Full standings table
- Stats Modal: Detailed statistics
- Clean design, easy to close

### 5. Ticker
- Simple at bottom
- Minimal styling

## Spacing Guidelines
- Hero content: 60px padding
- Cards: 20px gap
- Info cards: 24px gap
- Sections: 40px vertical spacing

## Blur Reduction
- Navbar: Light blur (10px)
- Cards: Minimal blur (5px) or solid backgrounds
- Modals: Light blur (15px)
- Remove excessive backdrop-filter

