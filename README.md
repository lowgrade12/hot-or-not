# ⚔️ Stash Battle Performer

A head-to-head performer comparison plugin for [Stash](https://stashapp.cc/) that uses an ELO-style rating system to help you rank your performers.

## Overview

Stash Battle Performer presents you with two performers side-by-side and asks you to pick the better one. Based on your choices, performer ratings are automatically updated using an ELO algorithm. Over time, this builds an accurate ranking of your entire performer library based on your personal preferences.

## Features

- **Three Comparison Modes:**
  - **Swiss** ⚖️ – Fair matchups between similarly-rated performers. Both performers' ratings adjust based on the outcome.
  - **Gauntlet** 🎯 – Place a random performer in your rankings. It climbs from the bottom, challenging each performer above it until it loses, then settles into its final position.
  - **Champion** 🏆 – Winner stays on. The winning performer keeps battling until it's dethroned.

## Installation

⚠️ Install at your own risk, nearly entirely vibe coded for myself using Claude, I have barely reviewed the code at all.

Recommend saving a backup of your database beforehand (Settings → Interface → Editing)

### Manual Download: 
1. Download the `/plugins/stash-battle-performer/` folder to your Stash plugins directory

## Usage

Optional Step: Change Rating System Type to "Decimal" (Settings → Interface → Editing)
1. Navigate to the **Performers** page in Stash
2. Click the floating ⚔️ button in the bottom-right corner
3. Choose your preferred comparison mode
4. Click on a performer (or use arrow keys) to pick the winner
5. Watch your rankings evolve over time!

## How It Works

The plugin uses an ELO-inspired algorithm where:
- Beating a higher-rated performer earns more points than beating a lower-rated one
- Losing to a lower-rated performer costs more points than losing to a higher-rated one
- Ratings are stored in Stash's native `rating100` field (1-100 scale which is why changing to decimal rating system type is recommended)

## Requirements

- At least 2 performers in your library

## Credits

This plugin is a fork of [stash-battle](https://github.com/dtt-git/stash-battle) by dtt-git, adapted to work with performers instead of scenes.

## License

See [LICENCE](LICENCE) for details.
