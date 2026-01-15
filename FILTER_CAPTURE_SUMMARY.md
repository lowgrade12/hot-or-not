# Filter Capture Implementation Summary

## Problem Statement
The HotOrNot plugin's filter capture was not working properly. Filters needed to be captured dynamically when users navigate or change filters, not just when the modal is opened.

## Solution
Implemented `PluginApi.Event.addEventListener("stash:location", ...)` as suggested in the problem statement to capture filter changes dynamically.

## Implementation Details

### 1. Event Listener for Location Changes
```javascript
PluginApi.Event.addEventListener("stash:location", (e) => {
  console.log("[HotOrNot] Page changed:", e.detail.data.location.pathname);
  
  // Update cached filter when on performers page
  const path = e.detail.data.location.pathname;
  if (path === '/performers' || path === '/performers/') {
    // Parse current filters from URL
    const newFilter = getUrlPerformerFilter();
    
    // Only update cache if modal is not currently open
    const modalOpen = document.getElementById("hon-modal") !== null;
    if (!modalOpen) {
      cachedUrlFilter = newFilter;
      // ... logging ...
    }
  }
});
```

**Key Features:**
- Listens for Stash's `stash:location` events
- Accesses pathname via `e.detail.data.location.pathname`
- Updates cached filter when on performers page
- Preserves modal session by not updating when modal is open

### 2. Enhanced Logging
Added detailed console logging to help debug filter issues:

- `parseUrlFilterCriteria()`: Logs raw, decoded, and parsed criteria
- `getUrlPerformerFilter()`: Logs criterion-to-filter conversion
- `openRankingModal()`: Logs filter detection status
- Event listener: Logs page changes and filter updates

### 3. Backward Compatibility
The implementation includes safety checks:

```javascript
if (typeof PluginApi !== 'undefined' && PluginApi.Event && PluginApi.Event.addEventListener) {
  // Add event listener
}
```

This ensures the plugin works even if:
- PluginApi is not available
- Older Stash versions don't have Event.addEventListener
- Plugin runs in non-Stash environment

In these cases, the plugin falls back to the original behavior (parsing filters only when modal opens).

## Benefits

1. **Dynamic Filter Updates:** Filters are captured whenever the user navigates or changes them
2. **Better Debugging:** Enhanced logging makes it easier to diagnose filter issues
3. **Session Preservation:** Modal sessions aren't disrupted by external filter changes
4. **Backward Compatible:** Works with older Stash versions

## Testing

See [TESTING_FILTERS.md](TESTING_FILTERS.md) for comprehensive testing instructions.

## Files Modified

- `plugins/hotornot/hotornot.js`:
  - Added event listener in `init()` function
  - Enhanced logging in `parseUrlFilterCriteria()`
  - Enhanced logging in `getUrlPerformerFilter()`
  - Updated comments in `openRankingModal()`

## Files Created

- `TESTING_FILTERS.md`: Comprehensive testing documentation
- `FILTER_CAPTURE_SUMMARY.md`: This file

## Technical Notes

### URL Filter Format
Stash encodes filters in the URL using the `c` parameter:
- Format: `?c={"type":"tags","value":{"items":["id1"],"depth":0},"modifier":"INCLUDES"}`
- Can be JSON array or custom encoded format
- Plugin handles both formats

### Event Timing
- `stash:location` events fire when:
  - User navigates to a different page
  - URL changes (including filter changes)
  - History state changes

### Filter Cache Strategy
1. **On Init:** No filters cached (waits for first navigation event)
2. **On Location Change:** Parse and cache filters (if on performers page and modal closed)
3. **On Modal Open:** Refresh filters from current URL
4. **During Modal Session:** Preserve cached filters (don't update)

This ensures filters are always current while preventing session disruption.

## Future Improvements

Potential enhancements for future versions:

1. **Support for Complex Filter Logic:** Handle AND/OR/NOT combinations
2. **Real-time Filter Updates:** Update comparisons when filters change mid-session (optional)
3. **Filter Validation:** Validate filter format before caching
4. **Filter Diff Logging:** Log what changed when filters update
5. **Filter Persistence:** Remember last used filters across sessions

## References

- Stash PluginApi Documentation: https://docs.stashapp.cc/in-app-manual/plugins/uipluginapi/
- PluginApi.Event.addEventListener example from problem statement
- Stash v0.25.0 release notes (introduced stash:location event)
