# Project Goals

## Vision

Create a personal, interactive dashboard for a jailbroken Kindle Paperwhite that displays useful information in an e-ink optimized format, refreshing automatically via GitHub Actions.

## Primary Goals

### Phase 1: Core Dashboard (Current)
- [x] Weather display with current conditions and forecast
- [x] Time and date display
- [x] Reminders/to-do list from text file
- [ ] Rotating e-ink optimized artwork
- [ ] GitHub Actions auto-generation every 15 minutes
- [ ] GitHub Pages hosting

### Phase 2: Enhanced Features
- [ ] Visual calendar (month/week/day views)
- [ ] Google Tasks integration
- [ ] Multiple layout modes
- [ ] Weather forecast graph/visualization

### Phase 3: Advanced
- [ ] Custom screensaver integration
- [ ] Multiple dashboard "pages"
- [ ] External API integrations
- [ ] SSH-based remote control

## Non-Goals (Out of Scope)
- Real-time updates (e-ink refresh limitations make this impractical)
- Color display (device is grayscale only)
- Video or animations
- Complex interactive elements

## Success Criteria
1. Dashboard displays correctly on Kindle PW 11th Gen
2. Automatic refresh works reliably via GitHub Actions
3. Easy to customize (edit config.yml, reminders.txt)
4. Artwork rotation provides visual variety
5. Battery impact is minimal (refresh every 15+ minutes)

## Technical Constraints
- Display: 1236 × 1648 pixels, 16-level grayscale
- Refresh: ~1 second full refresh, partial available
- Network: WiFi only, fetches static PNG
- Storage: Limited (~6 GB total)
- Processing: Minimal on-device (all rendering server-side)
