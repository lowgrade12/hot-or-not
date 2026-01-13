# HotOrNot Plugin

A plugin for [Stash](https://stashapp.cc/) that uses an ELO-style rating system to help you rank performers and images.

## 🔥 HotOrNot (Performers & Images)

A head-to-head comparison plugin that helps you rank performers and images.

**Features:**
- **Three Comparison Modes:**
  - **Swiss** ⚖️ – Fair matchups between similarly-rated items. Both ratings adjust based on the outcome.
  - **Gauntlet** 🎯 – Place a random item in your rankings. They climb from the bottom, challenging each item above them until they lose, then settle into their final position.
  - **Champion** 🏆 – Winner stays on. The winning item keeps battling until they're dethroned.
- **Advanced Performer Filtering** ⚙️ – Filter performers by gender, ethnicity, country, age, rating, name, and more!

## Overview

The plugin presents you with two performers or images side-by-side and asks you to pick the better one. Based on your choices, ratings are automatically updated using an ELO algorithm. Over time, this builds an accurate ranking of your entire library based on your personal preferences.

## Installation

⚠️ Install at your own risk, nearly entirely vibe coded for myself using Claude, I have barely reviewed the code at all.

Recommend saving a backup of your database beforehand (Settings → Interface → Editing)

### Manual Download: 
1. Download the `/plugins/hotornot/` folder to your Stash plugins directory

## Usage

Optional Step: Change Rating System Type to "Decimal" (Settings → Interface → Editing)

### For Performers:
1. Navigate to the **Performers** page in Stash
2. Click the floating 🔥 button in the bottom-right corner
3. **(Optional)** Click the filter panel to customize which performers appear in comparisons
4. Choose your preferred comparison mode
4. Click on a performer (or use arrow keys) to pick the winner
5. Watch your rankings evolve over time!

### For Images:
1. Navigate to the **Images** page in Stash
2. Click the floating 🔥 button in the bottom-right corner
3. Choose your preferred comparison mode
4. Click on an image (or use arrow keys) to pick the winner
5. Watch your rankings evolve over time!

## Advanced Performer Filtering

When comparing performers, you can use the built-in filter panel to narrow down which performers appear in your comparisons. This is perfect for creating focused rankings or comparing specific groups.

### Available Filters:

#### 🎭 Gender
Select which genders to include in comparisons:
- Female
- Trans Female
- Non-Binary
- Male
- Trans Male
- Intersex

**Default:** Only Female performers (for backward compatibility)

#### 🌍 Ethnicity
Filter by ethnicity using text search (e.g., "Asian", "Caucasian", "Latina", "Ebony")
- Leave empty to include all ethnicities
- Searches within performer ethnicity field

#### 🗺️ Country
Filter by country using text search (e.g., "USA", "Japan", "Brazil", "Czech Republic")
- Leave empty to include all countries
- Searches within performer country field

#### 🎂 Age Range
Set minimum and/or maximum age for performers
- Range: 18-100 years
- Based on performer birthdate
- Leave empty for no age restriction

#### ⭐ Rating Range
Filter by existing rating (1-100 scale)
- Useful for comparing only highly-rated or unrated performers
- Leave empty to include all ratings

#### 🔍 Name Search
Search for specific performers by name
- Useful for finding and comparing particular performers
- Partial name matching supported

#### 🖼️ Image Requirement
Toggle whether performers must have profile images
- **Checked (default):** Only show performers with images
- **Unchecked:** Include all performers regardless of image

### Using Filters:

1. Click the **⚙️ Filter Performers** panel to expand it
2. Adjust any filters you want to apply
3. Click **Apply Filters** to load new comparisons with your filter settings
4. Click **Reset** to return to default settings (Female only, must have image)

**Note:** Changing filters will reset any active Gauntlet or Champion run.

## How It Works

The plugin uses an ELO-inspired algorithm where:
- Beating a higher-rated item earns more points than beating a lower-rated one
- Losing to a lower-rated item costs more points than losing to a higher-rated one
- Ratings are stored in Stash's native `rating100` field (1-100 scale which is why changing to decimal rating system type is recommended)

## Requirements

- At least 2 performers or images in your library (depending on which page you're on)

## Credits

- **HotOrNot** - Inspired by [stash-battle](https://github.com/dtt-git/stash-battle) by dtt-git, adapted for performer and image ranking

## License

See [LICENCE](LICENCE) for details.
