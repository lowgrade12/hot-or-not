# Filter Enhancement Summary

## Changes Made

### 1. Gender Filter Support ✅

**Problem:** Gender filter was protected and couldn't be overridden by user filters. The plugin always excluded males by default.

**Solution:** 
- Removed `gender` from `PROTECTED_FILTER_KEYS` constant
- Added explicit gender filter handling in `convertToPerformerFilter()`
- Gender filter can now be set by users with any value (MALE, FEMALE, etc.) and any modifier (INCLUDES, EXCLUDES)

**Implementation:**
```javascript
// Before
const PROTECTED_FILTER_KEYS = new Set(['gender', 'NOT']);

// After
const PROTECTED_FILTER_KEYS = new Set(['NOT']);

// New filter handler
if (criteria.type === 'gender') {
  const genderValue = criteria.value?.value || criteria.value;
  if (genderValue) {
    filter.gender = {
      value: genderValue,
      modifier: criteria.modifier || 'INCLUDES'
    };
  }
}
```

**Usage Example:**
```
?c=("type":"gender","modifier":"INCLUDES","value":"FEMALE")
?c=("type":"gender","modifier":"EXCLUDES","value":"MALE")
```

### 2. BETWEEN Modifier Support ✅

**Problem:** Users wanted to filter performers by rating range (e.g., rating between 20-30) but BETWEEN modifier wasn't supported.

**Solution:**
- Added special handling for `BETWEEN` modifier in rating100 filter
- Checks for both `value` and `value2` properties
- Validates both values are within 0-100 range
- Falls back to single-value handling for other modifiers

**Implementation:**
```javascript
if (criteria.type === 'rating100') {
  // Handle BETWEEN modifier (requires value and value2)
  if (criteria.modifier === 'BETWEEN' && 
      criteria.value?.value !== undefined && 
      criteria.value?.value2 !== undefined) {
    const ratingValue = parseFloat(criteria.value.value);
    const ratingValue2 = parseFloat(criteria.value.value2);
    if (!isNaN(ratingValue) && !isNaN(ratingValue2) && 
        ratingValue >= 0 && ratingValue <= 100 && 
        ratingValue2 >= 0 && ratingValue2 <= 100) {
      filter.rating100 = {
        value: ratingValue,
        value2: ratingValue2,
        modifier: 'BETWEEN'
      };
    }
  }
  // Handle other modifiers...
}
```

**Usage Example:**
```
?c=("type":"rating100","modifier":"BETWEEN","value":("value":20,"value2":30))
```

### 3. Country Filter Fix ✅

**Problem:** Country filter wasn't working reliably due to inconsistent value structure in different scenarios.

**Solution:**
- Enhanced country filter to handle both nested value structure (`value.value`) and direct value
- Uses fallback logic: `criteria.value?.value || criteria.value`
- More robust parsing of country filter data

**Implementation:**
```javascript
// Before
if (criteria.type === 'country' && criteria.value?.value) {
  filter.country = {
    value: criteria.value.value,
    modifier: criteria.modifier || 'EQUALS'
  };
}

// After
if (criteria.type === 'country') {
  const countryValue = criteria.value?.value || criteria.value;
  if (countryValue) {
    filter.country = {
      value: countryValue,
      modifier: criteria.modifier || 'EQUALS'
    };
  }
}
```

**Usage Example:**
```
?c=("type":"country","modifier":"EQUALS","value":("value":"United States"))
?c=("type":"country","modifier":"EQUALS","value":"Canada")
```

## Files Modified

1. **plugins/hotornot/hotornot.js**
   - Line 21-22: Removed gender from PROTECTED_FILTER_KEYS
   - Lines 1145-1178: Enhanced rating100 filter with BETWEEN modifier support
   - Lines 1219-1242: Fixed country filter and added gender filter
   - Line 1245: Updated supportedTypes array to include 'gender'
   - Lines 1252-1258: Updated getPerformerFilter() comments

2. **ACTIVE_FILTER_IMPLEMENTATION.md**
   - Added "Recent Enhancements" section documenting new features
   - Updated supported filter types list
   - Updated filter modifiers list with BETWEEN
   - Updated getPerformerFilter documentation

3. **test_new_filters.html** (NEW)
   - Created comprehensive test page for validating new filter functionality
   - Tests gender filter (INCLUDES and EXCLUDES)
   - Tests BETWEEN modifier for rating100
   - Tests country filter (nested and direct value formats)
   - Tests combined filters

## Testing

### Manual Testing
Open `test_new_filters.html` in a browser and run the following tests:

1. **Gender Filter Test**
   - Click "Test Gender Filter (FEMALE)" - should show `gender.value = "FEMALE"`
   - Click "Test Gender Filter (EXCLUDES MALE)" - should show `gender.modifier = "EXCLUDES"`

2. **BETWEEN Modifier Test**
   - Click "Test BETWEEN Filter (20-30)" - should show `rating100: {value: 20, value2: 30, modifier: "BETWEEN"}`
   - Click "Test BETWEEN Filter (50-80)" - should show proper range

3. **Country Filter Test**
   - Click "Test Country Filter (Nested Value)" - should extract "United States"
   - Click "Test Country Filter (Direct Value)" - should extract "Canada"

4. **Combined Filters Test**
   - Click "Test Gender + Rating BETWEEN + Country" - should show all three filters applied

### Integration Testing in Stash
To test in actual Stash environment:

1. Navigate to Performers page
2. Apply gender filter (e.g., INCLUDES FEMALE)
3. Open HotOrNot plugin - should show only female performers
4. Apply rating filter with BETWEEN modifier (20-30)
5. Open HotOrNot plugin - should show only performers with rating between 20-30
6. Apply country filter (e.g., United States)
7. Open HotOrNot plugin - should respect country filter

## Compatibility

- **Stash Version:** v0.27+ (requires custom fields API)
- **Backward Compatible:** Yes - existing filters continue to work
- **Breaking Changes:** None - only adds new functionality

## Default Behavior

The default behavior remains the same:
- Performers without images are still excluded (NOT filter)
- Males are excluded by default UNLESS user explicitly sets gender filter
- When gender filter is set, it overrides the default

## Notes

- All three requested features are now fully implemented
- Console logging added for debugging filter application
- Comprehensive validation ensures invalid values are rejected
- Fallback logic makes filters more robust to varying data structures
