# HotOrNot Plugin Versions

This repository provides two versions of the HotOrNot plugin. Choose the one that best fits your needs.

## 🔥 Version Comparison

| Feature | Basic | With Filtering |
|---------|-------|----------------|
| **Location** | `/plugins/hotornot/` | `/plugins/hotornot-filtering/` |
| **Version** | 1.0.0 | 1.1.0 |
| **ELO Ranking** | ✅ | ✅ |
| **Three Comparison Modes** | ✅ | ✅ |
| **Performer Comparisons** | ✅ | ✅ |
| **Image Comparisons** | ✅ | ✅ |
| **Gender Filtering** | ❌ | ✅ |
| **Ethnicity Filtering** | ❌ | ✅ |
| **Country Filtering** | ❌ | ✅ |
| **Age Range Filtering** | ❌ | ✅ |
| **Rating Range Filtering** | ❌ | ✅ |
| **Name Search** | ❌ | ✅ |
| **Image Requirement Toggle** | ❌ | ✅ |

## 📦 Version 1: HotOrNot (Basic)

**Best for:** Simple, straightforward usage without customization needs

### Features
- ELO-based ranking system
- Three comparison modes (Swiss, Gauntlet, Champion)
- Works with performers and images
- Lightweight and fast
- No configuration needed

### Who Should Use This
- Users who want simple head-to-head comparisons
- Those who don't need to filter their comparison pool
- Users preferring a minimal, streamlined experience

### Installation
Download the `/plugins/hotornot/` folder to your Stash plugins directory.

## 🎯 Version 2: HotOrNot with Filtering (Advanced)

**Best for:** Users who want granular control over their comparison pool

### Features
Everything from the basic version PLUS:

#### 🎭 **Gender Filter**
Select specific gender identities to include in comparisons:
- Female, Trans Female, Non-Binary, Male, Trans Male, Intersex

#### 🌍 **Demographic Filters**
- **Ethnicity**: Filter by ethnic background
- **Country**: Filter by country of origin

#### 📊 **Range Filters**
- **Age Range**: Set minimum and maximum age (18-100)
- **Rating Range**: Compare only performers within a specific rating tier

#### 🔍 **Search & Requirements**
- **Name Search**: Find specific performers by name
- **Image Requirement**: Toggle whether performers need profile images

### Who Should Use This
- Users with large performer libraries
- Those who want to create focused rankings (e.g., "Top Asian Performers")
- Users who want to filter by demographics
- Anyone wanting more control over comparison matchups

### Installation
Download the `/plugins/hotornot-filtering/` folder to your Stash plugins directory.

### Documentation
For complete filtering documentation, see [FILTERING_GUIDE.md](FILTERING_GUIDE.md)

## ⚠️ Important Notes

### Installation Guidelines

1. **Install Only One Version at a Time**
   - Both plugins use the same UI elements and will conflict if installed simultaneously
   - If you want to switch versions, remove one before installing the other

2. **Backup Your Database**
   - Both versions modify the `rating100` field
   - Recommend backing up your Stash database before installation

3. **No Data Migration Needed**
   - Ratings are stored in Stash's native `rating100` field
   - You can switch between versions without losing ranking data

### Choosing Between Versions

**Choose Basic Version if:**
- You want the simplest experience
- You don't need filtering options
- You prefer minimal UI elements
- You're comparing your entire library

**Choose Filtering Version if:**
- You have a large library and want to focus on specific groups
- You want to create multiple separate rankings (e.g., by country or age)
- You need demographic filtering
- You want to exclude or include specific performer types

### Switching Between Versions

To switch from one version to another:

1. Remove the current plugin folder from your Stash plugins directory
2. Restart Stash (or reload plugins if your version supports it)
3. Add the new plugin folder
4. Restart Stash again

Your existing ratings will be preserved since they're stored in Stash's database, not the plugin.

## 🚀 Future Development

Both versions will be maintained in this repository:
- **Basic Version**: Will remain stable and lightweight
- **Filtering Version**: May receive additional filter types and features

If you discover issues or have feature requests, please open an issue on GitHub.

## 📝 Version History

### Version 1.1.0 (Filtering) - January 2026
- Added comprehensive filtering system
- 7 different filter types
- Collapsible filter UI
- Full documentation

### Version 1.0.0 (Basic) - Previous
- Initial release
- Core ELO ranking system
- Three comparison modes
- Performer and image support
