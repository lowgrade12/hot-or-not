(function () {
  "use strict";

  // ============================================
  // TOP PERFORMER PLUGIN
  // Displays the performer with the highest number of appearances for a studio
  // ============================================

  // Cache for top performers to avoid repeated API calls
  // Map<studioId, { performerName: string, sceneCount: number, timestamp: number }>
  const topPerformerCache = new Map();

  // Cache TTL in milliseconds (5 minutes)
  const CACHE_TTL = 5 * 60 * 1000;

  // ============================================
  // GRAPHQL HELPERS
  // ============================================

  async function graphqlQuery(query, variables = {}) {
    const response = await fetch("/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query, variables }),
    });
    const result = await response.json();
    if (result.errors) {
      console.error("[TopPerformer] GraphQL error:", result.errors);
      throw new Error(result.errors[0].message);
    }
    return result.data;
  }

  /**
   * Get the top performer for a studio by querying scenes and aggregating performer appearances
   * @param {string} studioId - The studio's ID
   * @returns {Promise<{name: string, count: number}|null>} Top performer info or null
   */
  async function getTopPerformerForStudio(studioId) {
    // Check cache first
    const cached = topPerformerCache.get(studioId);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      return { name: cached.performerName, count: cached.sceneCount };
    }

    try {
      // Query scenes for this studio with performer data
      // We use a large per_page to get all scenes, but limit for performance
      // Include gender field to filter out male performers
      const query = `
        query FindScenesForStudio($scene_filter: SceneFilterType, $filter: FindFilterType) {
          findScenes(scene_filter: $scene_filter, filter: $filter) {
            count
            scenes {
              id
              performers {
                id
                name
                gender
              }
            }
          }
        }
      `;

      const variables = {
        scene_filter: {
          studios: {
            value: [studioId],
            modifier: "INCLUDES"
          }
        },
        filter: {
          // Limit to 1000 scenes for performance - sufficient for most studios
          // The top performer in 1000 scenes is statistically representative
          per_page: 1000
        }
      };

      const result = await graphqlQuery(query, variables);
      const scenes = result.findScenes.scenes || [];

      if (scenes.length === 0) {
        return null;
      }

      // Aggregate performer appearances (excluding male performers)
      const performerCounts = new Map(); // Map<performerId, { name: string, count: number }>

      for (const scene of scenes) {
        for (const performer of scene.performers) {
          // Skip male performers (gender is "MALE" in Stash GraphQL)
          if (performer.gender === "MALE") {
            continue;
          }
          const existing = performerCounts.get(performer.id);
          if (existing) {
            existing.count++;
          } else {
            performerCounts.set(performer.id, { name: performer.name, count: 1 });
          }
        }
      }

      // Find the performer with the highest count
      let topPerformer = null;
      let maxCount = 0;

      for (const [, performerData] of performerCounts) {
        if (performerData.count > maxCount) {
          maxCount = performerData.count;
          topPerformer = performerData;
        }
      }

      if (topPerformer) {
        // Cache the result
        topPerformerCache.set(studioId, {
          performerName: topPerformer.name,
          sceneCount: topPerformer.count,
          timestamp: Date.now()
        });

        return { name: topPerformer.name, count: topPerformer.count };
      }

      return null;
    } catch (err) {
      console.error("[TopPerformer] Error fetching top performer for studio:", studioId, err);
      return null;
    }
  }

  /**
   * Get top performers for multiple studios in parallel
   * @param {string[]} studioIds - Array of studio IDs
   * @returns {Promise<Map<string, {name: string, count: number}>>} Map of studio ID to top performer info
   */
  async function getTopPerformersForStudios(studioIds) {
    const results = new Map();
    const uncachedIds = [];

    // Check cache first
    for (const studioId of studioIds) {
      const cached = topPerformerCache.get(studioId);
      if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
        results.set(studioId, { name: cached.performerName, count: cached.sceneCount });
      } else {
        uncachedIds.push(studioId);
      }
    }

    // Fetch uncached studios in parallel with error handling
    if (uncachedIds.length > 0) {
      const promises = uncachedIds.map(async (studioId) => {
        try {
          const topPerformer = await getTopPerformerForStudio(studioId);
          return { studioId, topPerformer, success: true };
        } catch (err) {
          console.warn("[TopPerformer] Failed to fetch top performer for studio:", studioId, err);
          return { studioId, topPerformer: null, success: false };
        }
      });

      const settled = await Promise.allSettled(promises);
      for (const result of settled) {
        if (result.status === "fulfilled" && result.value.topPerformer) {
          results.set(result.value.studioId, result.value.topPerformer);
        }
      }
    }

    return results;
  }

  // ============================================
  // STUDIO CARD DETECTION & INJECTION
  // ============================================

  /**
   * Extract studio ID from a studio card element
   * @param {HTMLElement} card - Studio card element
   * @returns {string|null} Studio ID or null
   */
  function getStudioIdFromCard(card) {
    // Try getting from card's link href (e.g., /studios/123)
    const link = card.querySelector("a[href*='/studios/']");
    if (link) {
      const href = link.getAttribute("href");
      const match = href.match(/\/studios\/(\d+)/);
      if (match) {
        return match[1];
      }
    }

    // Try data attributes
    if (card.dataset.studioId) {
      return card.dataset.studioId;
    }

    return null;
  }

  /**
   * Check if top performer widget already exists on card
   * @param {HTMLElement} card - Studio card element
   * @returns {boolean} True if widget exists
   */
  function hasTopPerformerWidget(card) {
    return card.querySelector(".tp-top-performer") !== null;
  }

  /**
   * Create the top performer display element
   * @param {string} performerName - Name of the top performer
   * @param {number} sceneCount - Number of scenes
   * @returns {HTMLElement} The top performer element
   */
  function createTopPerformerElement(performerName, sceneCount) {
    const container = document.createElement("div");
    container.className = "tp-top-performer";
    
    const icon = document.createElement("span");
    icon.className = "tp-icon";
    icon.innerHTML = "👑"; // Crown emoji for top performer
    
    const nameSpan = document.createElement("span");
    nameSpan.className = "tp-name";
    nameSpan.textContent = performerName;
    
    const countSpan = document.createElement("span");
    countSpan.className = "tp-count";
    countSpan.textContent = `(${sceneCount} scenes)`;
    
    container.appendChild(icon);
    container.appendChild(nameSpan);
    container.appendChild(countSpan);
    
    return container;
  }

  /**
   * Inject top performer widget into studio card
   * @param {HTMLElement} card - Studio card element
   * @param {{name: string, count: number}|null} topPerformer - Pre-fetched top performer info
   */
  async function injectTopPerformerWidget(card, topPerformer = undefined) {
    if (hasTopPerformerWidget(card)) {
      return;
    }

    const studioId = getStudioIdFromCard(card);
    if (!studioId) {
      console.warn("[TopPerformer] Could not get studio ID from card");
      return;
    }

    try {
      // Fetch top performer if not provided
      if (topPerformer === undefined) {
        topPerformer = await getTopPerformerForStudio(studioId);
      }

      if (!topPerformer) {
        // No performers found for this studio
        card.dataset.tpProcessed = "true";
        return;
      }

      // Create and inject the widget
      const widget = createTopPerformerElement(topPerformer.name, topPerformer.count);

      // Find the best place to inject (in the card content area)
      const cardContent = card.querySelector(".studio-card-content") ||
                          card.querySelector(".card-section") ||
                          card.querySelector(".card-body") ||
                          card;

      // Try to insert at the end of the card content
      cardContent.appendChild(widget);

      // Mark card as processed
      card.dataset.tpProcessed = "true";
    } catch (err) {
      console.error("[TopPerformer] Error injecting widget:", err);
    }
  }

  /**
   * Process all studio cards on the page
   */
  async function processStudioCards() {
    // Various selectors for studio cards in Stash UI
    const cardSelectors = [
      ".studio-card",
      "[class*='StudioCard']",
      ".card.studio",
      ".grid-item.studio"
    ];

    let cards = [];
    for (const selector of cardSelectors) {
      const found = document.querySelectorAll(selector);
      if (found.length > 0) {
        cards = Array.from(found);
        break;
      }
    }

    // Alternative: look for cards that have studio links
    if (cards.length === 0) {
      const allCards = document.querySelectorAll(".card");
      cards = Array.from(allCards).filter(card => {
        const link = card.querySelector("a[href*='/studios/']");
        return link !== null;
      });
    }

    // Filter to only unprocessed cards
    const unprocessedCards = cards.filter(card => !card.dataset.tpProcessed);
    if (unprocessedCards.length === 0) {
      return;
    }

    // Collect studio IDs for batch query
    const cardIdMap = new Map(); // studioId -> card
    for (const card of unprocessedCards) {
      const studioId = getStudioIdFromCard(card);
      if (studioId) {
        cardIdMap.set(studioId, card);
      }
    }

    const studioIds = Array.from(cardIdMap.keys());
    if (studioIds.length === 0) {
      return;
    }

    try {
      // Fetch top performers for all studios
      const topPerformers = await getTopPerformersForStudios(studioIds);

      // Inject widgets for each card
      for (const [studioId, card] of cardIdMap.entries()) {
        const topPerformer = topPerformers.get(studioId);
        await injectTopPerformerWidget(card, topPerformer || null);
      }
    } catch (err) {
      console.error("[TopPerformer] Error processing cards in batch:", err);
      // Fallback to individual processing
      for (const card of unprocessedCards) {
        await injectTopPerformerWidget(card);
      }
    }
  }

  // ============================================
  // PAGE DETECTION
  // ============================================

  /**
   * Check if we're on a scene-related page where the top performer widget should not appear
   * This includes individual scene pages and scene listing pages
   * @returns {boolean} True if on a scene-related page
   */
  function isSceneRelatedPage() {
    const path = window.location.pathname;
    // Match /scenes - main scenes listing page (with or without query params)
    if (path === "/scenes" || path === "/scenes/") {
      return true;
    }
    // Match /scenes/123 or /scenes/123/... patterns (scene ID followed by slash or end of path)
    if (/^\/scenes\/\d+(?:\/|$)/.test(path)) {
      return true;
    }
    // Match /studios/{id}/scenes - scene listing page for a specific studio
    if (/^\/studios\/\d+\/scenes(?:\/|$|\?)/.test(path)) {
      return true;
    }
    // Match /performers/{id}/scenes - scene listing page for a specific performer
    if (/^\/performers\/\d+\/scenes(?:\/|$|\?)/.test(path)) {
      return true;
    }
    return false;
  }

  /**
   * Check if we're on a page that may have studio cards
   * This includes the studios page and the main/home page
   * @returns {boolean} True if on a page that may show studios
   */
  function isPageWithPotentialStudios() {
    const path = window.location.pathname;
    // Studios page
    if (path === "/studios" || path === "/studios/" || path.startsWith("/studios?")) {
      return true;
    }
    // Main/home page - may show studios
    if (path === "/" || path === "") {
      return true;
    }
    return false;
  }

  /**
   * Check if studio cards are present on the page
   * @returns {boolean} True if studio cards are detected
   */
  function hasStudioCardsOnPage() {
    // Various selectors for studio cards in Stash UI
    // Use querySelector (returns first match) instead of querySelectorAll for efficiency
    const cardSelectors = [
      ".studio-card",
      "[class*='StudioCard']",
      ".card.studio",
      ".grid-item.studio"
    ];

    for (const selector of cardSelectors) {
      if (document.querySelector(selector)) {
        return true;
      }
    }

    // Check for cards that have studio links using a more specific selector
    if (document.querySelector(".card a[href*='/studios/']")) {
      return true;
    }

    return false;
  }

  /**
   * Check if we should process studio cards on this page
   * @returns {boolean} True if we should process studio cards
   */
  function shouldProcessStudios() {
    // Never show on scene-related pages
    if (isSceneRelatedPage()) {
      return false;
    }
    return isPageWithPotentialStudios() || hasStudioCardsOnPage();
  }

  // ============================================
  // INITIALIZATION
  // ============================================

  // Debounce timeout for mutation observer
  let processingTimeout = null;

  /**
   * Initialize the plugin
   */
  function init() {
    console.log("[TopPerformer] Plugin initialized");

    // Initial processing if on a page with potential studios
    if (shouldProcessStudios()) {
      // Delay to allow Stash UI to render
      setTimeout(() => {
        processStudioCards();
      }, 1000);
    }

    // Watch for DOM changes (SPA navigation, lazy loading, etc.)
    const observer = new MutationObserver((mutations) => {
      // Check if we should process - either on studios/main page OR if studio cards exist
      if (!shouldProcessStudios()) {
        return;
      }

      // Debounce processing
      clearTimeout(processingTimeout);
      processingTimeout = setTimeout(() => {
        processStudioCards();
      }, 500);
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    // Listen for Stash navigation events if PluginApi is available
    if (typeof PluginApi !== "undefined" && PluginApi.Event && PluginApi.Event.addEventListener) {
      PluginApi.Event.addEventListener("stash:location", (e) => {
        console.log("[TopPerformer] Page changed:", e.detail.data.location.pathname);

        if (shouldProcessStudios()) {
          // Delay to allow UI to render
          setTimeout(() => {
            processStudioCards();
          }, 500);
        }
      });
    }
  }

  // Start plugin
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
