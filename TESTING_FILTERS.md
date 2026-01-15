# Testing Filter Capture with PluginApi.Event

This document describes how to test the dynamic filter capture feature that uses `PluginApi.Event.addEventListener("stash:location", ...)`.

## What Was Fixed

Previously, the HotOrNot plugin only captured URL filters when the modal was opened. This meant:
- If you applied filters AFTER opening the modal, they wouldn't be detected
- If you navigated to a different page with filters, the plugin wouldn't update
- The plugin relied solely on parsing URL parameters at modal open time

Now, the plugin listens for Stash's `stash:location` events and dynamically updates the cached filters whenever you navigate or change filters.

## How to Test

### Test 1: Filters Applied Before Opening Modal

1. Navigate to the Performers page (`/performers`)
2. Apply some filters (e.g., filter by a tag, studio, or favorite status)
3. Open the browser console (F12) and look for HotOrNot log messages
4. Click the 🔥 button to open the HotOrNot modal
5. **Expected Result:** 
   - Console should show: `[HotOrNot] Using URL filters for performers: {...}`
   - Only performers matching your filters should appear in comparisons
   - Console should show detailed logging of filter parsing

### Test 2: Filter Changes While Navigating

1. Navigate to the Performers page
2. Open the browser console (F12)
3. Apply a filter (e.g., filter by a tag)
4. **Expected Result:**
   - Console should show: `[HotOrNot] Page changed: /performers`
   - Console should show: `[HotOrNot] Updated cached filters: {...}`
5. Remove the filter or add another filter
6. **Expected Result:**
   - Console should show updated filter information
7. Click the 🔥 button to open HotOrNot
8. **Expected Result:**
   - Modal should use the latest filters from the URL

### Test 3: Modal Preserves Filters During Session

1. Navigate to Performers page with a filter applied
2. Open the HotOrNot modal (🔥 button)
3. While the modal is open, manually change the URL filter in the browser's address bar
4. **Expected Result:**
   - The modal should continue using the filters it was opened with
   - When you close and re-open the modal, it should use the new filters

### Test 4: No Filters Applied

1. Navigate to Performers page without any filters
2. Open the browser console
3. Click the 🔥 button
4. **Expected Result:**
   - Console should show: `[HotOrNot] No URL filters detected`
   - Plugin should use default filters (excluding males, excluding performers without images)

### Test 5: Images Page (No Filter Support)

1. Navigate to Images page (`/images`)
2. Click the 🔥 button
3. **Expected Result:**
   - Console should show: `[HotOrNot] No URL filters detected` (or similar)
   - Images should be shown in Swiss mode only
   - No filters should be applied (images don't support URL filtering in this plugin)

## Console Logging

The enhanced logging will show:

```
[HotOrNot] Initialized
[HotOrNot] Page changed: /performers
[HotOrNot] No filter criteria found in URL (no "c" parameter)
[HotOrNot] Converting 0 criteria to performer filter
[HotOrNot] Final performer filter: {}
[HotOrNot] Cleared cached filters (no filters active)
```

When filters are present:

```
[HotOrNot] Page changed: /performers
[HotOrNot] Raw filter criteria from URL: [{"type":"tags","value":...}]
[HotOrNot] Decoded filter criteria: [...]
[HotOrNot] Parsed criteria as JSON: [...]
[HotOrNot] Converting 1 criteria to performer filter
[HotOrNot] Converted criterion: {...} to filter part: {...}
[HotOrNot] Final performer filter: {...}
[HotOrNot] Updated cached filters: {...}
```

## What to Look For

### Success Indicators:
- ✅ Console shows filter updates when navigating/changing filters
- ✅ Modal uses correct filters when opened
- ✅ Only filtered performers appear in comparisons
- ✅ No JavaScript errors in console

### Failure Indicators:
- ❌ Console shows errors when parsing filters
- ❌ All performers appear even when filters are applied
- ❌ Filter changes don't update the cached filter
- ❌ JavaScript errors about PluginApi not being defined

## Troubleshooting

### If filters aren't working:

1. **Check the URL:** Make sure the URL contains a `?c=...` parameter when filters are applied
2. **Check Console Logs:** Look for `[HotOrNot]` messages to see what's being parsed
3. **Verify PluginApi:** Make sure your Stash version supports `PluginApi.Event.addEventListener`
4. **Check Filter Format:** Some filters might use a format not yet supported by the parser

### If PluginApi is not defined:

The plugin includes a check: `if (typeof PluginApi !== 'undefined' && PluginApi.Event && PluginApi.Event.addEventListener)`

This means if PluginApi is not available, the event listener simply won't be added, and the plugin will fall back to the original behavior (parsing filters only when modal opens).

## Known Limitations

1. **Modal Session Isolation:** When a modal is open, filter updates won't affect it (by design - to prevent disrupting an active session)
2. **Image Filters:** Images don't use URL filters in this plugin (performance optimization)
3. **Complex Filter Logic:** Some complex filter combinations (AND/OR/NOT logic) might not be fully supported yet

## Need Help?

If you encounter issues:
1. Check the browser console for `[HotOrNot]` log messages
2. Verify your Stash version supports PluginApi.Event
3. Try the tests above to isolate the issue
4. Report the issue with console logs and steps to reproduce
