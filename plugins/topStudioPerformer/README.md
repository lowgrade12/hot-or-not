# TopPerformer Plugin

> **Note**: This plugin is inspired by [studioTopPerformer](https://github.com/Serechops/Serechops-Stash/tree/main/plugins/studioTopPerformer).

A plugin for [Stash](https://stashapp.cc/) that displays the performer with the highest number of appearances for each studio directly on studio cards.

## Features

### Top Performer Display
- **Crown icon (👑)** to highlight the top performer
- **Performer name** displayed prominently
- **Scene count** showing how many scenes they appear in for that studio

### Smart Caching
- **5-minute cache** for top performer data
- Prevents repeated API calls for the same studio
- Cache is per-studio for efficient memory usage

### Gender Filtering
- **Excludes male performers** from the top performer calculation
- Focuses on primary performers for accurate studio representation

### Batch Processing
- **Parallel API calls** for multiple studios on the same page
- Error handling with fallback to individual processing
- Non-blocking operation that doesn't slow page load

### Page Detection
- **Automatic activation** on the Studios page
- **Works on the home page** if studios are displayed
- **Intelligently disabled** on scene-related pages where studio cards appear in a different context

## Installation

1. Download the `/plugins/topStudioPerformer/` folder to your Stash plugins directory
2. Reload plugins in Stash (Settings → Plugins → Reload)
3. Navigate to the Studios page to see the top performer on each studio card

## Usage

Simply browse the Studios page. The plugin automatically:
1. Detects studio cards on the page
2. Fetches scene data for each studio (up to 1000 scenes)
3. Aggregates performer appearances (excluding male performers)
4. Displays the top performer on each card

## Visual Appearance

The widget appears at the bottom of each studio card:
```
👑 Performer Name (45 scenes)
```

Styled to match the Stash UI with:
- Crown emoji indicator
- Performer name (bold)
- Scene count in parentheses

## Technical Details

### Scene Fetching
- Queries up to **1000 scenes** per studio for statistical accuracy
- Uses GraphQL with studio filter
- Aggregates performer appearances from all scenes

### Card Detection
The plugin detects studio cards using:
- `.studio-card`
- `[class*='StudioCard']`
- `.card.studio`
- `.grid-item.studio`
- Cards with `/studios/` links

### Page Filtering
The plugin is **disabled** on:
- `/scenes` - Scene listing pages
- `/scenes/{id}` - Individual scene pages
- `/studios/{id}/scenes` - Studio scene listings
- `/performers/{id}/scenes` - Performer scene listings

This prevents showing the widget on studio cards that appear in scene-related contexts.

### Performance
- **Parallel processing** for all studios on the page
- **Promise.allSettled** for graceful error handling
- **Mutation Observer** watches for DOM changes (lazy loading, pagination)

## Requirements

- Stash v0.27 or later
- Works on the `/studios` page and home page

## Limitations

- Processes a maximum of 1000 scenes per studio (sufficient for most studios)
- Gender filtering only excludes "MALE" - other genders are included
- Cache expires after 5 minutes; manual refresh may show stale data briefly

## License

See [LICENCE](../../LICENCE) for details.

## Credits

This plugin is inspired by [studioTopPerformer](https://github.com/Serechops/Serechops-Stash/tree/main/plugins/studioTopPerformer).
