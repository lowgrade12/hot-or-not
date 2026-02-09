# Set Stashbox Favorites Plugin

> **Note**: This plugin is inspired by [stashSetStashboxFavoritePerformers](https://github.com/lowgrade12/hotornottest/tree/main/plugins/stashSetStashboxFavoritePerformers).

A plugin for [Stash](https://stashapp.cc/) that synchronizes your favorite performers and studios with StashDB (stashdb.org). When you mark a performer or studio as a favorite in Stash, it automatically updates their favorite status on StashDB.

## Features

### Automatic Sync (Hooks)
- **Performer favorites** - Automatically syncs to StashDB when you update a performer in Stash
- **Studio favorites** - Automatically syncs to StashDB when you update a studio in Stash
- **Real-time updates** - Changes are pushed immediately via `Performer.Update.Post` and `Studio.Update.Post` hooks

### Manual Sync (Tasks)
- **Bulk performer sync** - Sync all favorite performers to StashDB at once
- **Bulk studio sync** - Sync all favorite studios to StashDB at once

### Error Handling
- **Invalid StashID tagging** - Optionally tag performers/studios with invalid or missing StashDB IDs
- **Configurable tag name** - Customize the tag used to mark invalid entries

## Installation

1. Download the `/plugins/setStashboxFavorites/` folder to your Stash plugins directory
2. Reload plugins in Stash (Settings → Plugins → Reload)
3. Configure your StashDB API key in Settings → Plugins

## Configuration

### Settings

| Setting | Description |
|---------|-------------|
| **Tag performers/studios with invalid stashids** | When enabled, adds a tag to performers/studios that have invalid or missing StashDB IDs |
| **Invalid stashid tag name** | The name of the tag to apply to invalid entries |

### StashDB Configuration

The plugin requires a configured StashDB endpoint in Stash:
1. Go to Settings → Metadata Providers → Stash-box Endpoints
2. Add or verify the StashDB endpoint: `https://stashdb.org/graphql`
3. Enter your StashDB API key

## Usage

### Automatic Sync

Once installed, the plugin automatically syncs favorites when you:
1. Mark a performer as favorite/unfavorite in Stash
2. Mark a studio as favorite/unfavorite in Stash

The change is pushed to StashDB immediately (requires the performer/studio to have a valid StashDB stash_id).

### Manual Bulk Sync

To sync all favorites at once:

1. Go to Settings → Tasks → Plugin Tasks
2. Run **"Set Stashbox Favorite Performers"** to sync all performer favorites
3. Run **"Set Stashbox Favorite Studios"** to sync all studio favorites

## Requirements

- Stash v0.27 or later
- A StashDB account with API key
- Performers/studios must have valid StashDB stash_ids to sync

### Dependencies

The plugin uses the following Python dependencies:
- `stashapi` (included with Stash)
- `ssl`, `urllib` (Python standard library)

## How It Works

1. **On Update Hook**: When a performer/studio is updated:
   - Fetches the performer/studio details including stash_ids
   - Checks if they have a StashDB stash_id
   - Retrieves your StashDB API key from Stash configuration
   - Calls the StashDB API to set the favorite status

2. **Bulk Sync Task**: When manually triggered:
   - Queries all performers/studios marked as favorites in Stash
   - For each with a valid StashDB stash_id, updates the favorite status on StashDB
   - Optionally tags entries with invalid stash_ids

## Troubleshooting

### Favorites not syncing

1. **Check StashDB configuration**: Ensure you have the StashDB endpoint configured with a valid API key
2. **Verify stash_id**: The performer/studio must have a valid StashDB stash_id
3. **Check logs**: Enable debug logging to see detailed sync information

### Invalid StashID Tag

If performers/studios are being tagged as invalid:
1. They may not have been matched to StashDB yet
2. Run a metadata scrape to match them with StashDB
3. The stash_id may have been removed from StashDB

## License

See [LICENCE](../../LICENCE) for details.

## Credits

This plugin is inspired by [stashSetStashboxFavoritePerformers](https://github.com/lowgrade12/hotornottest/tree/main/plugins/stashSetStashboxFavoritePerformers).

Based on the [stash-plugins](https://github.com/7dJx1qP/stash-plugins) repository by 7dJx1qP.
