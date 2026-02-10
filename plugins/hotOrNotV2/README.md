# HotOrNotV2 Plugin

An ELO-based ranking system for performers in [Stash](https://stashapp.cc/). Compare performers head-to-head in an interactive battle interface to build personalized rankings based on your preferences.

## Features

### Battle Modes

The plugin offers three distinct comparison modes:

#### 🎯 Swiss Mode (Default)
- **True ELO with zero-sum property** - Winner gains exactly what loser loses, maintaining rating pool integrity
- Pairs performers with similar ratings for competitive matchups
- Uses weighted random selection to prioritize performers with fewer matches
- Best for building initial rankings and ensuring balanced coverage

#### 🏆 Gauntlet Mode
- **King of the hill style** - One performer stays on as champion while challengers attempt to dethrone them
- Champion works their way up the rankings by defeating increasingly difficult opponents
- Only the active participant (champion) has their rating change
- When the champion loses, they "fall" to find their appropriate position
- Visual streak tracking shows how many wins the current champion has
- Great for quickly identifying top performers

#### 👑 Champion Mode
- **Winner stays on** with reduced rating impact (50% of Swiss mode)
- Both performers get rating updates, but at a slower pace
- Maintains the "winner stays on" excitement while still evolving rankings
- Good for fine-tuning existing rankings

### ELO Rating System

- **Adaptive K-factor** based on:
  - Match count (new performers have higher K-factor for faster initial placement)
  - Scene count (prolific performers have more stable ratings)
  - Current rating distance from default
- **Diminishing returns** at high ratings (harder to reach 100)
- **Skip as draw** - Skipping applies ELO draw mechanics (higher-rated performer loses points to lower-rated)

### Comprehensive Statistics

Each performer tracks:
- Total matches played
- Wins, losses, and draws
- Current streak (positive = winning, negative = losing)
- Best and worst streaks ever
- Last match timestamp

Access the **Stats Modal** to view:
- Rating distribution bar chart (grouped by rating ranges)
- Full leaderboard with all performers
- Win rates and streak information

### URL Filter Support

Respects the current page's filter criteria when launched from a filtered performers page:
- Gender filters
- Tag filters
- Studio filters
- Rating filters
- Favorites filter
- Age, ethnicity, country filters
- And many more...

### User Interface

- **Floating action button** on performer pages to launch the comparison modal
- **Battle rank badge** on individual performer pages showing their rank position (e.g., "#5 of 100")
- **Side-by-side comparison** with performer images and metadata
- **Visual feedback** showing rating changes after each choice
- **Keyboard shortcuts**: Left Arrow (choose left), Right Arrow (choose right), Escape (close)
- **Responsive design** that works on desktop and mobile
- **Video preview on hover** for performers with preview clips

### Battle Rank Badge

When viewing a single performer's page, a badge displays their battle rank:
- Shows rank position and total performers (e.g., "Battle Rank #5 of 100")
- Tier-based styling: 👑 Legendary (top 5%), 🥇 Gold (top 20%), 🥈 Silver (top 40%), 🥉 Bronze (top 60%), 🔥 Default
- Hover for tooltip showing exact rating

## Installation

1. Download the `/plugins/hotOrNotV2/` folder to your Stash plugins directory
2. Reload plugins in Stash (Settings → Plugins → Reload)
3. Navigate to the Performers page to see the floating HotOrNot button

## Usage

1. Go to the Performers page in Stash
2. Optionally apply filters to narrow down the performer pool
3. Click the floating HotOrNot button (🔥) in the bottom-right corner
4. Select your preferred battle mode
5. Click on a performer or their "Choose" button to select the winner
6. Continue rating until you're satisfied with your rankings

### Tips

- **First run**: Swiss mode with many comparisons builds a solid ranking foundation
- **Quick ranking**: Gauntlet mode rapidly identifies your top performers
- **Fine-tuning**: Champion mode adjusts rankings with smaller changes
- **Skip strategically**: Use skip when you can't decide - it affects both performers' ratings based on ELO draw mechanics

## Custom Fields

The plugin stores match statistics in a custom field called `hotornot_stats` containing:
```json
{
  "total_matches": 42,
  "wins": 25,
  "losses": 15,
  "draws": 2,
  "current_streak": 3,
  "best_streak": 8,
  "worst_streak": -4,
  "last_match": "2024-01-15T10:30:00.000Z"
}
```

## Requirements

- Stash v0.27 or later
- Performers must have images for best experience (performers without images are excluded by default)

## Technical Details

### Rating Scale
- Ratings are stored as `rating100` (0-100 scale)
- Displayed as 0.0-10.0 in the UI
- Default rating for unrated performers: 50 (5.0)

### K-Factor Calculation
| Match Count | Base K-Factor |
|-------------|---------------|
| 0-9 matches | 16 |
| 10-29 matches | 12 |
| 30+ matches | 8 |

Scene count multipliers further reduce K-factor for established performers.

### Default Filters
When no URL filters are applied, the plugin automatically:
- Excludes male performers
- Excludes performers without images

## License

See [LICENCE](../../LICENCE) for details.
