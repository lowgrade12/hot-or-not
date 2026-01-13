# HotOrNot Plugin

A plugin for [Stash](https://stashapp.cc/) that uses an ELO-style rating system to help you rank performers and images.

## 🔥 HotOrNot (Performers & Images)

A head-to-head comparison plugin that helps you rank performers and images.

**Features:**
- **Three Comparison Modes:**
  - **Swiss** ⚖️ – Fair matchups between similarly-rated items. Both ratings adjust based on the outcome.
  - **Gauntlet** 🎯 – Place a random item in your rankings. They climb from the bottom, challenging each item above them until they lose, then settle into their final position.
  - **Champion** 🏆 – Winner stays on. The winning item keeps battling until they're dethroned.

## Overview

The plugin presents you with two performers or images side-by-side and asks you to pick the better one. Based on your choices, ratings are automatically updated using an ELO algorithm. Over time, this builds an accurate ranking of your entire library based on your personal preferences.

## Available Versions

This repository contains two plugin versions. See [PLUGIN_VERSIONS.md](PLUGIN_VERSIONS.md) for a detailed comparison.

### 1. **HotOrNot** (Basic Version)
- **Location**: `/plugins/hotornot/`
- **Best for**: Simple, straightforward performer/image comparisons
- **Features**: Core ELO ranking with three comparison modes

### 2. **HotOrNot with Filtering** (Advanced Version) 🆕
- **Location**: `/plugins/hotornot-filtering/`
- **Best for**: Users who want to customize their comparison pool
- **Features**: Everything in the basic version PLUS advanced filtering options
  - Filter by gender, ethnicity, country
  - Filter by age range and rating range
  - Search by performer name
  - Toggle image requirements
- **Documentation**: See [FILTERING_GUIDE.md](FILTERING_GUIDE.md) for complete details

⚠️ **Important**: Both versions can be installed, but **only install one at a time** to avoid conflicts.

## Installation

⚠️ Install at your own risk, nearly entirely vibe coded for myself using Claude, I have barely reviewed the code at all.

Recommend saving a backup of your database beforehand (Settings → Interface → Editing)

### Manual Download: 

**For Basic Version:**
1. Download the `/plugins/hotornot/` folder to your Stash plugins directory

**For Advanced Version with Filtering:**
1. Download the `/plugins/hotornot-filtering/` folder to your Stash plugins directory

## Usage

Optional Step: Change Rating System Type to "Decimal" (Settings → Interface → Editing)

### For Performers:
1. Navigate to the **Performers** page in Stash
2. Click the floating 🔥 button in the bottom-right corner
3. Choose your preferred comparison mode
4. Click on a performer (or use arrow keys) to pick the winner
5. Watch your rankings evolve over time!

### For Images:
1. Navigate to the **Images** page in Stash
2. Click the floating 🔥 button in the bottom-right corner
3. Choose your preferred comparison mode
4. Click on an image (or use arrow keys) to pick the winner
5. Watch your rankings evolve over time!

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
