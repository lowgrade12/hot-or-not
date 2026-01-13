# Performer Filtering Guide

This document provides detailed information about the performer filtering system in HotOrNot plugin.

## Overview

The filtering system allows you to customize which performers appear in your head-to-head comparisons. This is useful for:

- Creating focused rankings for specific groups
- Comparing only highly-rated performers
- Filtering by demographic characteristics
- Excluding or including specific performer attributes

## Filter Types

### 1. Gender Filter 🎭

**Type:** Multi-select checkboxes  
**GraphQL Modifier:** `INCLUDES` or `EXCLUDES`  
**Default:** Female only (for backward compatibility)

Select which gender identities to include in comparisons:

- **Female** - Cisgender female performers
- **Trans Female** - Transgender female performers  
- **Non-Binary** - Non-binary performers
- **Male** - Cisgender male performers
- **Trans Male** - Transgender male performers
- **Intersex** - Intersex performers

**How it works:**
- If no genders are selected, defaults to excluding males (legacy behavior)
- If one or more genders are selected, only those genders will appear
- Multiple selections work with OR logic (performer matches ANY selected gender)

**Use cases:**
- Compare only female performers
- Include all gender identities for inclusive rankings
- Focus on transgender performers specifically
- Create separate rankings for different gender groups

---

### 2. Ethnicity Filter 🌍

**Type:** Text input  
**GraphQL Modifier:** `INCLUDES`  
**Default:** Empty (all ethnicities)

Filter performers by their ethnicity field using text search.

**Examples:**
- "Asian" - Performers with Asian ethnicity
- "Caucasian" - Performers with Caucasian ethnicity
- "Latina" - Performers with Latina/Latino ethnicity
- "Ebony" - Performers with Ebony/Black ethnicity
- "Mixed" - Performers with mixed ethnicity

**How it works:**
- Performs a text search within the performer's ethnicity field
- Case-insensitive matching
- Partial matches are included
- Leave empty to include all ethnicities

**Use cases:**
- Create ethnicity-specific rankings
- Focus comparisons on performers of a particular background
- Study preferences across different ethnic groups

---

### 3. Country Filter 🗺️

**Type:** Text input  
**GraphQL Modifier:** `INCLUDES`  
**Default:** Empty (all countries)

Filter performers by their country of origin using text search.

**Examples:**
- "USA" or "United States"
- "Japan"
- "Brazil"
- "Czech Republic"
- "Russia"

**How it works:**
- Performs a text search within the performer's country field
- Case-insensitive matching
- Partial matches are included
- Leave empty to include all countries

**Use cases:**
- Create country-specific rankings
- Compare performers from a particular region
- Focus on international vs. domestic performers

---

### 4. Age Range Filter 🎂

**Type:** Numeric range (min/max)  
**GraphQL Modifier:** `BETWEEN`, `GREATER_THAN`, or `LESS_THAN`  
**Default:** Empty (all ages)  
**Valid Range:** 18-100 years

Filter performers by their current age (calculated from birthdate).

**Options:**
- **Min Age:** Minimum age (e.g., 21 for performers 21 and older)
- **Max Age:** Maximum age (e.g., 35 for performers 35 and younger)
- **Both:** Set both to create a specific age range (e.g., 25-35)

**How it works:**
- Calculates age from performer's birthdate field
- Converts age to birthdate range for GraphQL query
- Performers without birthdates are excluded when filter is active

**Use cases:**
- Compare only performers in a specific age bracket
- Create "young performers" or "experienced performers" rankings
- Study age-related preferences
- Filter out performers outside your preferred age range

---

### 5. Rating Range Filter ⭐

**Type:** Numeric range (min/max)  
**GraphQL Modifier:** `BETWEEN`, `GREATER_THAN`, or `LESS_THAN`  
**Default:** Empty (all ratings)  
**Valid Range:** 1-100

Filter performers by their existing rating100 value.

**Options:**
- **Min Rating:** Minimum rating (e.g., 70 for highly-rated performers)
- **Max Rating:** Maximum rating (e.g., 30 for lower-rated performers)
- **Both:** Set both to create a specific rating range (e.g., 60-80)

**How it works:**
- Filters based on the current rating100 field value
- Useful for refining rankings within a specific tier
- Can be used to find and compare unrated performers (rating < 10)

**Use cases:**
- Compare only your top-rated performers
- Find hidden gems among mid-tier performers
- Create "championship rounds" with only 90+ rated performers
- Focus on unrated or new performers
- Re-rank a specific tier of your library

---

### 6. Name Search Filter 🔍

**Type:** Text input  
**GraphQL Modifier:** `INCLUDES`  
**Default:** Empty (all names)

Search for specific performers by name.

**Examples:**
- "Riley" - Find all performers with "Riley" in their name
- "Alexis" - Find all "Alexis" performers
- "Anna" - Partial name matching

**How it works:**
- Performs a text search within the performer's name field
- Case-insensitive matching
- Partial matches are included
- Useful for comparing performers with similar names

**Use cases:**
- Find and compare specific performers
- Create head-to-head matchups between performers
- Test your preferences among performers you're considering
- Compare performers with similar stage names

---

### 7. Image Requirement Toggle 🖼️

**Type:** Boolean checkbox  
**GraphQL Modifier:** `NOT is_missing: "image"`  
**Default:** Checked (require images)

Control whether performers must have profile images to appear in comparisons.

**Options:**
- **Checked (default):** Only include performers who have profile images
- **Unchecked:** Include all performers regardless of image availability

**How it works:**
- When checked, filters out performers with missing image data
- Ensures visual comparisons are always possible
- Unchecking allows comparing performers without images (shows placeholder)

**Use cases:**
- Keep visual consistency in comparisons (default)
- Include all performers in rankings even without images
- Find performers that need images added
- Create text-based comparisons when images aren't important

---

## Filter Combinations

Filters can be combined for powerful, targeted comparisons:

### Example Combinations:

**1. "Top Asian Performers"**
- Ethnicity: "Asian"
- Min Rating: 80
- Require Image: Yes

**2. "Young American Talent"**
- Country: "USA"
- Max Age: 25
- Require Image: Yes

**3. "Transgender Performers Championship"**
- Gender: Trans Female, Trans Male
- Min Rating: 70
- Require Image: Yes

**4. "Brazilian Performers Showcase"**
- Country: "Brazil"
- Require Image: Yes

**5. "Mature Performers"**
- Min Age: 35
- Min Rating: 50
- Require Image: Yes

## Technical Details

### GraphQL Filter Structure

The filters are converted to Stash's GraphQL `PerformerFilterType` with appropriate modifiers:

```javascript
{
  gender: { value: ["FEMALE"], modifier: "INCLUDES" },
  ethnicity: { value: "Asian", modifier: "INCLUDES" },
  country: { value: "Japan", modifier: "INCLUDES" },
  birth_date: { value: "1990-01-01", modifier: "GREATER_THAN" },
  rating100: { value: 70, modifier: "GREATER_THAN" },
  name: { value: "Yuki", modifier: "INCLUDES" },
  NOT: { is_missing: "image" }
}
```

### Filter Modifiers

- **INCLUDES** - Field contains/matches the value
- **EXCLUDES** - Field does not contain/match the value
- **BETWEEN** - Field value is between value and value2
- **GREATER_THAN** - Field value is greater than value
- **LESS_THAN** - Field value is less than value

## Best Practices

1. **Start Broad, Then Narrow** - Begin with loose filters, then tighten as needed
2. **Save Filter Settings** - Document successful filter combinations for future use
3. **Test Filter Results** - Use "Apply Filters" and check the comparison pool size
4. **Reset When Stuck** - Use "Reset" button if you get "not enough performers" errors
5. **Combine Thoughtfully** - Too many filters can result in no performers matching
6. **Image Requirement** - Keep this checked for best visual experience
7. **Age Filters** - Ensure birthdates are populated in your Stash database

## Troubleshooting

**"Not enough performers for comparison"**
- Your filters are too restrictive
- Try removing some filters or broadening ranges
- Click "Reset" to return to defaults
- Ensure at least 2 performers match your criteria

**No performers match my filters**
- Check that performer data is populated in Stash
- Verify spelling in text filters
- Try partial name searches instead of full names
- Remove ethnicity/country filters if uncertain of exact values

**Filters not applying**
- Click "Apply Filters" button after making changes
- Check for status message confirmation
- Reload the modal if needed (close and reopen)

## Future Enhancements

Potential future filter additions:
- Height range filter
- Weight range filter
- Hair color filter
- Eye color filter
- Cup size filter (for applicable performers)
- Tag-based filtering
- Studio filtering
- Scene count filtering
- Favorite/unfavorite status
- Custom date ranges
- Multiple ethnicity selection
- Preset filter combinations

---

## Summary

The HotOrNot performer filtering system provides 7 different filter types that can be combined to create highly customized comparison experiences:

1. **Gender** - Multi-select checkboxes for gender identity
2. **Ethnicity** - Text search for ethnic background
3. **Country** - Text search for country of origin
4. **Age Range** - Min/max age based on birthdate
5. **Rating Range** - Min/max rating filter
6. **Name Search** - Find performers by name
7. **Image Requirement** - Require profile images

These filters enable targeted rankings, focused comparisons, and customized experiences based on your preferences and library composition.
