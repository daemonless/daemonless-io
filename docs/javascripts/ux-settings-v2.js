// Catalog Scope/Category/Slug Filtering, Live Deployment Customizer, and Status Helpers
// Instant-navigation safe via Zensical's document$ observable.
(function () {
  const FLEET_VIEW_STORAGE_KEY = "daemonless-fleet-view";
  const DEPLOY_PREFS_KEY = "daemonless:deploy-prefs";
  const DEPLOY_PORT_PREFIX = "daemonless:port:";

  const DEFAULT_PREFS = {
    configRoot: "/containers",
    registry: "ghcr.io/daemonless",
    puid: "1000",
    pgid: "1000",
    tz: "UTC",
  };

  const SCOPE_LABELS = {
    apps: "Applications",
    stacks: "Multi-Service Stacks",
    appliances: "Network Appliances",
    base: "Base & CLI Images",
    all: "All Images",
  };

  let expandedParents = new Set();

  const fold = (s) => (s || "").toLowerCase().replace(/[-_\s]+/g, "");

  function matchesFoldedQuery(haystack, rawQuery) {
    if (!rawQuery) return true;
    const h = fold(haystack);
    const tokens = rawQuery.trim().split(/\s+/).map(fold).filter(Boolean);
    return tokens.every((t) => h.includes(t));
  }

  // ── 1. Live Deployment Customizer (on /images/<app>/) ──────────────────────
  function readDeployPrefs() {
    try {
      const saved = JSON.parse(localStorage.getItem(DEPLOY_PREFS_KEY) || "{}");
      return Object.assign({}, DEFAULT_PREFS, saved);
    } catch (_) {
      return Object.assign({}, DEFAULT_PREFS);
    }
  }

  function writeDeployPrefs(prefs) {
    try {
      localStorage.setItem(DEPLOY_PREFS_KEY, JSON.stringify(prefs));
    } catch (_) {}
  }

  function readAppPort(app, fallback) {
    if (!fallback) return "";
    try {
      return localStorage.getItem(DEPLOY_PORT_PREFIX + app) || fallback;
    } catch (_) {
      return fallback;
    }
  }

  function writeAppPort(app, val, fallback) {
    try {
      if (!val || val === fallback) localStorage.removeItem(DEPLOY_PORT_PREFIX + app);
      else localStorage.setItem(DEPLOY_PORT_PREFIX + app, val);
    } catch (_) {}
  }

  function deploymentElements(details) {
    const out = [];
    const heading = document.getElementById("deployment");
    let cur = heading ? heading.nextElementSibling : details;
    while (cur && cur.tagName !== "H2") {
      out.push(cur);
      cur = cur.nextElementSibling;
    }
    return out;
  }

  function rewriteText(orig, cfg) {
    let s = orig;
    if (cfg.defaultRegistry && cfg.registry && cfg.registry !== cfg.defaultRegistry) {
      s = s.split(cfg.defaultRegistry).join(cfg.registry);
    }
    if (cfg.configRoot && cfg.configRoot !== "/containers") {
      s = s.replace(/\/containers(?=\/|\b)/g, cfg.configRoot);
    }
    if (cfg.hasUid) {
      if (cfg.puid && cfg.puid !== "1000") {
        s = s.replace(/\bPUID=1000\b/g, "PUID=" + cfg.puid)
             .replace(/\bPUID:\s*1000\b/g, "PUID: " + cfg.puid)
             .replace(/\bPUID="1000"/g, 'PUID="' + cfg.puid + '"');
      }
      if (cfg.pgid && cfg.pgid !== "1000") {
        s = s.replace(/\bPGID=1000\b/g, "PGID=" + cfg.pgid)
             .replace(/\bPGID:\s*1000\b/g, "PGID: " + cfg.pgid)
             .replace(/\bPGID="1000"/g, 'PGID="' + cfg.pgid + '"');
      }
    }
    if (cfg.tz && cfg.tz !== "UTC") {
      s = s.replace(/\bTZ=UTC\b/g, "TZ=" + cfg.tz)
           .replace(/\bTZ:\s*UTC\b/g, "TZ: " + cfg.tz)
           .replace(/\bTZ="UTC"/g, 'TZ="' + cfg.tz + '"');
    }
    if (cfg.defaultPort && cfg.port && cfg.port !== cfg.defaultPort) {
      const dp = cfg.defaultPort.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      s = s.replace(new RegExp("(^|\\s|-p\\s+|\"|-\\s+)" + dp + ":" + dp + "(?=\\b|\"|/tcp|/udp)", "g"), "$1" + cfg.port + ":" + cfg.defaultPort)
           .replace(new RegExp(":" + dp + "=" + dp + "\\b", "g"), ":" + cfg.port + "=" + cfg.defaultPort)
           .replace(new RegExp("_PORT=" + dp + "\\b", "g"), "_PORT=" + cfg.port);
    }
    return s;
  }

  function applySplitSpanReplacements(codeEl, cfg) {
    const spans = Array.from(codeEl.querySelectorAll("span"));
    for (let i = 0; i < spans.length; i++) {
      const sp = spans[i];
      if (sp._dlSpanOrig === undefined) sp._dlSpanOrig = sp.textContent;
      const key = sp._dlSpanOrig;
      let targetVal = null;
      let expectedDefault = null;
      if (cfg.hasUid && key === "PUID") { targetVal = cfg.puid; expectedDefault = "1000"; }
      else if (cfg.hasUid && key === "PGID") { targetVal = cfg.pgid; expectedDefault = "1000"; }
      else if (key === "TZ") { targetVal = cfg.tz; expectedDefault = "UTC"; }
      else if (cfg.defaultPort && key.endsWith("_PORT")) { targetVal = cfg.port; expectedDefault = cfg.defaultPort; }
      if (!targetVal || !expectedDefault) continue;

      let next = sp.nextSibling;
      while (next && next.textContent.trim() === "") next = next.nextSibling;
      if (!next || !next.textContent.includes("=")) continue;
      let valNode = next.nextSibling;
      while (valNode && valNode.textContent.trim() === "") valNode = valNode.nextSibling;
      if (!valNode) continue;
      if (valNode._dlValOrig === undefined) valNode._dlValOrig = valNode.textContent;
      if (valNode._dlValOrig === expectedDefault) {
        valNode.textContent = targetVal;
      } else if (valNode._dlValOrig === '"' + expectedDefault + '"') {
        valNode.textContent = '"' + targetVal + '"';
      }
    }
  }

  function applyDeployCustomizations(details) {
    const app = details.dataset.app || "";
    const defaultRegistry = details.dataset.defaultRegistry || "ghcr.io/daemonless";
    const defaultPort = details.dataset.defaultPort || "";
    const hasUid = details.dataset.hasUid === "true";
    const prefs = readDeployPrefs();
    const port = readAppPort(app, defaultPort);

    const cleanRoot = (prefs.configRoot || "/containers").replace(/\/+$/, "") || "/containers";
    const cleanReg = (prefs.registry || defaultRegistry).replace(/\/+$/, "") || defaultRegistry;

    const cfg = {
      defaultRegistry,
      registry: cleanReg,
      configRoot: cleanRoot,
      hasUid,
      puid: (prefs.puid || "1000").trim() || "1000",
      pgid: (prefs.pgid || "1000").trim() || "1000",
      tz: (prefs.tz || "UTC").trim() || "UTC",
      defaultPort,
      port: (port || defaultPort).trim() || defaultPort,
    };

    const isModified =
      cfg.configRoot !== "/containers" ||
      cfg.registry !== defaultRegistry ||
      (hasUid && (cfg.puid !== "1000" || cfg.pgid !== "1000")) ||
      cfg.tz !== "UTC" ||
      (defaultPort && cfg.port !== defaultPort);

    details.classList.toggle("is-modified", Boolean(isModified));

    const containers = deploymentElements(details);
    containers.forEach((root) => {
      if (root === details) return;
      root.querySelectorAll("code").forEach((codeEl) => {
        const walker = document.createTreeWalker(codeEl, NodeFilter.SHOW_TEXT);
        const nodes = [];
        let n;
        while ((n = walker.nextNode())) nodes.push(n);
        nodes.forEach((tn) => {
          if (tn._dlOrig === undefined) tn._dlOrig = tn.nodeValue;
          const nextVal = rewriteText(tn._dlOrig, cfg);
          if (tn.nodeValue !== nextVal) tn.nodeValue = nextVal;
        });
        applySplitSpanReplacements(codeEl, cfg);
      });
    });
  }

  function initDeployCustomizer() {
    const details = document.querySelector("details.deploy-customizer");
    if (!details) return;
    if (details._bound) {
      applyDeployCustomizations(details);
      return;
    }
    details._bound = true;

    const app = details.dataset.app || "";
    const defaultRegistry = details.dataset.defaultRegistry || "ghcr.io/daemonless";
    const defaultPort = details.dataset.defaultPort || "";
    const hasUid = details.dataset.hasUid === "true";
    const prefs = readDeployPrefs();
    const port = readAppPort(app, defaultPort);

    const body = details.querySelector(".deploy-customizer__body");
    if (!body) return;

    const fields = [
      { id: "configRoot", label: "Config Root", value: prefs.configRoot, placeholder: "/containers" },
      { id: "registry", label: "Registry", value: prefs.registry, placeholder: defaultRegistry },
    ];
    if (hasUid) {
      fields.push(
        { id: "puid", label: "PUID", value: prefs.puid, placeholder: "1000", inputmode: "numeric" },
        { id: "pgid", label: "PGID", value: prefs.pgid, placeholder: "1000", inputmode: "numeric" }
      );
    }
    fields.push({ id: "tz", label: "Timezone", value: prefs.tz, placeholder: "UTC" });
    if (defaultPort) {
      fields.push({ id: "port", label: "Host Port", value: port, placeholder: defaultPort, inputmode: "numeric" });
    }

    body.innerHTML =
      '<div class="deploy-customizer__grid">' +
      fields.map((f) =>
        '<label class="deploy-customizer__field">' +
        '<span>' + f.label + '</span>' +
        '<input type="text" data-cust-field="' + f.id + '" value="' + (f.value || "").replace(/"/g, "&quot;") + '" placeholder="' + f.placeholder + '"' + (f.inputmode ? ' inputmode="' + f.inputmode + '"' : "") + '>' +
        '</label>'
      ).join("") +
      '</div>' +
      '<div class="deploy-customizer__actions">' +
      '<span class="deploy-customizer__hint">Updates Compose, CLI, AppJail, and ZIP downloads live.</span>' +
      '<button type="button" class="deploy-customizer__reset">Reset defaults</button>' +
      '</div>';

    body.addEventListener("input", (e) => {
      const inp = e.target.closest("input[data-cust-field]");
      if (!inp) return;
      const key = inp.dataset.custField;
      if (key === "port") {
        writeAppPort(app, inp.value.trim(), defaultPort);
      } else {
        const next = readDeployPrefs();
        next[key] = inp.value;
        writeDeployPrefs(next);
      }
      applyDeployCustomizations(details);
    });

    body.querySelector(".deploy-customizer__reset").addEventListener("click", () => {
      writeDeployPrefs(DEFAULT_PREFS);
      writeAppPort(app, "", defaultPort);
      body.querySelectorAll("input[data-cust-field]").forEach((inp) => {
        const k = inp.dataset.custField;
        inp.value = k === "port" ? defaultPort : (DEFAULT_PREFS[k] || "");
      });
      applyDeployCustomizations(details);
    });

    applyDeployCustomizations(details);
  }

  document.addEventListener("daemonless:choices-updated", () => {
    const details = document.querySelector("details.deploy-customizer");
    if (details && details._bound) applyDeployCustomizations(details);
  });

  // ── 2. Catalog Scope, Category, Folding, Slug Search & URL Sync ────────────
  function setFleetView(view) {
    const cardsView = document.getElementById("fleet-cards-view");
    const tableView = document.getElementById("fleet-table-view");
    if (!cardsView || !tableView) return;

    const isTable = view === "table";
    cardsView.hidden = isTable;
    tableView.hidden = !isTable;

    document.querySelectorAll(".fleet-view-btn").forEach((btn) => {
      const active = btn.dataset.view === (isTable ? "table" : "cards");
      btn.classList.toggle("active", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });

    try {
      localStorage.setItem(FLEET_VIEW_STORAGE_KEY, isTable ? "table" : "cards");
    } catch (_) {}
  }

  function itemEligibleInScope(scopesStr, partOf, scopeFilter, hasQuery) {
    const scopes = (scopesStr || "").split(/\s+/).filter(Boolean);
    if (partOf) {
      if (scopeFilter === "all") return true;
      if (hasQuery) return scopes.includes(scopeFilter);
      if (expandedParents.has(partOf)) {
        return scopeFilter === "apps" || scopeFilter === "stacks";
      }
      return false;
    }
    return scopes.includes(scopeFilter);
  }

  function syncCatalogUrl(scopeFilter, categoryFilter, rawQuery) {
    if (!document.getElementById("fleet-active-grid")) return;
    const params = new URLSearchParams(window.location.search);
    if (scopeFilter && scopeFilter !== "apps") params.set("scope", scopeFilter);
    else params.delete("scope");
    if (categoryFilter && categoryFilter !== "all") params.set("category", categoryFilter);
    else params.delete("category");
    if (rawQuery) params.set("q", rawQuery);
    else params.delete("q");
    const qs = params.toString();
    const nextUrl = window.location.pathname + (qs ? "?" + qs : "") + window.location.hash;
    if (nextUrl !== window.location.pathname + window.location.search + window.location.hash) {
      window.history.replaceState(null, "", nextUrl);
    }
  }

  function updateCategoryCountsForScope(activeGrid, scopeFilter, hasQuery) {
    const catBar = document.getElementById("fleet-category-bar");
    if (!catBar || !activeGrid) return;

    if (scopeFilter === "base") {
      catBar.hidden = true;
      return;
    }
    catBar.hidden = false;

    const counts = {};
    let totalInScope = 0;
    activeGrid.querySelectorAll(".fleet-card").forEach((card) => {
      if (!itemEligibleInScope(card.dataset.scopes, card.dataset.partOf || "", scopeFilter, hasQuery)) return;
      totalInScope++;
      const c = card.dataset.category || "";
      counts[c] = (counts[c] || 0) + 1;
    });

    catBar.querySelectorAll(".fleet-cat-tab").forEach((tab) => {
      const cat = tab.dataset.category;
      const badge = tab.querySelector(".fleet-cat-count");
      if (cat === "all") {
        if (badge) badge.textContent = String(totalInScope);
        tab.hidden = false;
      } else {
        const n = counts[cat] || 0;
        if (badge) badge.textContent = String(n);
        tab.hidden = n === 0 && !tab.classList.contains("active");
      }
    });
  }

  function updateExpandButtons() {
    document.querySelectorAll(".fleet-expand-btn[data-expand-parent]").forEach((btn) => {
      const parent = btn.dataset.expandParent;
      const open = expandedParents.has(parent);
      const count = btn.dataset.count || "";
      const noun = btn.dataset.noun || "parts";
      btn.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.textContent = (open ? "Hide " : "+") + count + " " + noun + (open ? " ▴" : " ▾");
    });
  }

  function updateTableFilters(syncUrl = true) {
    const input = document.getElementById("image-search");
    const rawQuery = input ? input.value.trim() : "";
    const hasQuery = rawQuery.length > 0;

    const scopeBtn = document.querySelector(".fleet-scope-btn.active");
    const scopeFilter = scopeBtn ? scopeBtn.dataset.scope : "apps";

    const statusChip = document.querySelector(".status-chip.active");
    const statusFilter = statusChip ? statusChip.dataset.filter : "all";
    const archChip = document.querySelector(".arch-chip.active");
    const archFilter = archChip ? archChip.dataset.arch : "all";

    const catTab = document.querySelector(".fleet-cat-tab.active");
    const categoryFilter = scopeFilter === "base" ? "all" : (catTab ? catTab.dataset.category : "all");

    const activeGrid = document.getElementById("fleet-active-grid");
    if (activeGrid) {
      updateCategoryCountsForScope(activeGrid, scopeFilter, hasQuery);
      updateExpandButtons();
    }

    // 1. Update Card View (on /images/)
    let activeCardMatches = 0;
    let scopeTotal = 0;
    if (activeGrid) {
      activeGrid.querySelectorAll(".fleet-card").forEach((card) => {
        const scopeOk = itemEligibleInScope(card.dataset.scopes, card.dataset.partOf || "", scopeFilter, hasQuery);
        if (scopeOk) scopeTotal++;
        const catMatch = categoryFilter === "all" || card.dataset.category === categoryFilter;
        const textMatch = matchesFoldedQuery(card.dataset.search || card.textContent, rawQuery);
        const show = scopeOk && catMatch && textMatch;
        card.hidden = !show;
        if (show) activeCardMatches++;
      });
    }

    const depSection = document.getElementById("fleet-deprecated-cards-section");
    const depGrid = document.getElementById("fleet-deprecated-grid");
    let depCardMatches = 0;
    if (depGrid) {
      depGrid.querySelectorAll(".fleet-card").forEach((card) => {
        const scopeOk = (card.dataset.scopes || "apps all").split(/\s+/).includes(scopeFilter);
        const catMatch = categoryFilter === "all" || card.dataset.category === categoryFilter;
        const textMatch = matchesFoldedQuery(card.dataset.search || card.textContent, rawQuery);
        const show = scopeOk && catMatch && textMatch;
        card.hidden = !show;
        if (show) depCardMatches++;
      });
      if (depSection) depSection.hidden = depCardMatches === 0;
    }

    // 2. Update Table View (both /images/ and /status/)
    document.querySelectorAll(".md-content table").forEach((table) => {
      const isCatalogTable = Boolean(table.closest("#fleet-table-view"));
      const isStatusTable = Boolean(table.closest(".status-table-wrap"));
      if (!isCatalogTable && !isStatusTable) return;

      let matchCount = 0;
      table.querySelectorAll("tbody tr").forEach((row) => {
        if (isCatalogTable) {
          const meta = row.querySelector(".fleet-row-meta");
          const scopesStr = meta ? meta.dataset.scopes : "apps all";
          const partOf = meta ? (meta.dataset.partOf || "") : "";
          const cat = meta ? meta.dataset.category : "";
          const scopeOk = itemEligibleInScope(scopesStr, partOf, scopeFilter, hasQuery);
          const catMatch = categoryFilter === "all" || cat === categoryFilter;
          const searchStr = (meta ? meta.dataset.search : "") + " " + row.textContent;
          const textMatch = matchesFoldedQuery(searchStr, rawQuery);
          const show = scopeOk && catMatch && textMatch;
          row.style.display = show ? "" : "none";
          if (show) matchCount++;
          return;
        }

        const meta = row.querySelector(".row-meta");
        const hasMeta = Boolean(meta);
        const isOutdated = hasMeta ? meta.classList.contains("status-outdated") : Boolean(row.querySelector(".outdated"));
        const hasAmd64 = hasMeta ? meta.classList.contains("has-amd64") : true;
        const hasArm64 = hasMeta ? meta.classList.contains("has-arm64") : true;
        const outdatedAmd64 = hasMeta ? meta.classList.contains("outdated-amd64") : isOutdated;
        const outdatedArm64 = hasMeta ? meta.classList.contains("outdated-arm64") : isOutdated;

        let statusMatch = true;
        if (statusFilter === "outdated") {
          if (archFilter === "amd64") statusMatch = outdatedAmd64;
          else if (archFilter === "arm64") statusMatch = outdatedArm64;
          else statusMatch = isOutdated;
        } else if (statusFilter === "current") {
          if (archFilter === "amd64") statusMatch = hasAmd64 && !outdatedAmd64;
          else if (archFilter === "arm64") statusMatch = hasArm64 && !outdatedArm64;
          else statusMatch = !isOutdated;
        }

        let archMatch = true;
        if (statusFilter === "all" && archFilter !== "all") {
          if (archFilter === "amd64") archMatch = hasAmd64;
          else if (archFilter === "arm64") archMatch = hasArm64;
        }

        const searchStr = (meta ? meta.dataset.search || "" : "") + " " + row.textContent;
        const textMatch = matchesFoldedQuery(searchStr, rawQuery);
        const show = statusMatch && archMatch && textMatch;
        row.style.display = show ? "" : "none";
        if (show) matchCount++;
      });

      const header = table.previousElementSibling;
      const isFiltering = hasQuery || statusFilter !== "all" || archFilter !== "all" || categoryFilter !== "all" || scopeFilter !== "apps";
      if (matchCount === 0 && isFiltering) {
        table.style.display = "none";
        if (header && (header.tagName.startsWith("H") || header.tagName === "P")) {
          header.style.display = "none";
          const prev = header.previousElementSibling;
          if (prev && prev.tagName.startsWith("H")) prev.style.display = "none";
        }
      } else {
        table.style.display = "";
        if (header && (header.tagName.startsWith("H") || header.tagName === "P")) {
          header.style.display = "";
          const prev = header.previousElementSibling;
          if (prev && prev.tagName.startsWith("H")) prev.style.display = "";
        }
      }
    });

    // 3. Update Toolbar Heading, Count & Empty State (on /images/)
    const headingEl = document.getElementById("fleet-heading");
    const countEl = document.getElementById("fleet-count");
    const emptyEl = document.getElementById("fleet-empty-state");
    if (headingEl && countEl && activeGrid) {
      headingEl.textContent = categoryFilter === "all" ? (SCOPE_LABELS[scopeFilter] || "Applications") : categoryFilter;
      if (hasQuery || categoryFilter !== "all") {
        countEl.textContent = "Showing " + activeCardMatches + " of " + scopeTotal + " FreeBSD OCI images";
      } else {
        countEl.textContent = activeCardMatches + " FreeBSD OCI images";
      }
      if (emptyEl) {
        emptyEl.hidden = (activeCardMatches + depCardMatches) > 0;
      }
      if (syncUrl) syncCatalogUrl(scopeFilter, categoryFilter, rawQuery);
    }
  }

  function initFleetCatalog() {
    const cardsView = document.getElementById("fleet-cards-view");
    if (!cardsView) return;

    expandedParents = new Set();

    let savedView = "cards";
    try {
      savedView = localStorage.getItem(FLEET_VIEW_STORAGE_KEY) || "cards";
    } catch (_) {}
    setFleetView(savedView === "table" ? "table" : "cards");

    const params = new URLSearchParams(window.location.search);
    const urlScope = params.get("scope") || "apps";
    const urlCat = params.get("category") || "all";
    const urlQuery = params.get("q") || "";

    const input = document.getElementById("image-search");
    if (input) input.value = urlQuery;

    const validScopes = Array.from(document.querySelectorAll(".fleet-scope-btn")).map((b) => b.dataset.scope);
    const activeScope = validScopes.includes(urlScope) ? urlScope : "apps";
    document.querySelectorAll(".fleet-scope-btn").forEach((btn) => {
      const active = btn.dataset.scope === activeScope;
      btn.classList.toggle("active", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });

    const validCats = Array.from(document.querySelectorAll(".fleet-cat-tab")).map((t) => t.dataset.category);
    const activeCat = validCats.includes(urlCat) ? urlCat : "all";
    document.querySelectorAll(".fleet-cat-tab").forEach((tab) => {
      const active = tab.dataset.category === activeCat;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-pressed", active ? "true" : "false");
    });

    updateTableFilters(false);
  }

  // ── 3. Status Timestamp Humanizer ──────────────────────────────────────────
  function humanizeLastCheck() {
    const el = document.getElementById("last-check");
    if (!el || el.dataset.humanized) return;
    const then = new Date(el.getAttribute("datetime"));
    if (isNaN(then)) return;
    const mins = Math.round((Date.now() - then.getTime()) / 60000);
    let rel;
    if (mins < 1) rel = "just now";
    else if (mins < 60) rel = mins + " min ago";
    else if (mins < 1440) rel = Math.round(mins / 60) + " h ago";
    else rel = Math.round(mins / 1440) + " d ago";
    el.dataset.humanized = "1";
    el.textContent = rel + " (" + el.textContent.trim() + ")";
  }

  // ── 4. Document-Level Delegated Listeners (bound once) ─────────────────────
  document.addEventListener("input", (e) => {
    if (e.target && e.target.id === "image-search") {
      updateTableFilters(true);
    }
  });

  document.addEventListener("click", (e) => {
    const expandBtn = e.target.closest(".fleet-expand-btn[data-expand-parent]");
    if (expandBtn) {
      e.preventDefault();
      e.stopPropagation();
      const parent = expandBtn.dataset.expandParent;
      if (expandedParents.has(parent)) expandedParents.delete(parent);
      else expandedParents.add(parent);
      updateTableFilters(false);
      return;
    }

    const scopeBtn = e.target.closest(".fleet-scope-btn");
    if (scopeBtn) {
      document.querySelectorAll(".fleet-scope-btn").forEach((b) => {
        const active = b === scopeBtn;
        b.classList.toggle("active", active);
        b.setAttribute("aria-pressed", active ? "true" : "false");
      });
      updateTableFilters(true);
      return;
    }

    const viewBtn = e.target.closest(".fleet-view-btn");
    if (viewBtn) {
      setFleetView(viewBtn.dataset.view);
      return;
    }

    const catTab = e.target.closest(".fleet-cat-tab");
    if (catTab) {
      document.querySelectorAll(".fleet-cat-tab").forEach((tab) => {
        const active = tab === catTab;
        tab.classList.toggle("active", active);
        tab.setAttribute("aria-pressed", active ? "true" : "false");
      });
      updateTableFilters(true);
      return;
    }

    const resetBtn = e.target.closest("#fleet-reset-filters");
    if (resetBtn) {
      expandedParents.clear();
      const input = document.getElementById("image-search");
      if (input) input.value = "";
      document.querySelectorAll(".fleet-scope-btn").forEach((b) => {
        const active = b.dataset.scope === "apps";
        b.classList.toggle("active", active);
        b.setAttribute("aria-pressed", active ? "true" : "false");
      });
      document.querySelectorAll(".fleet-cat-tab").forEach((tab) => {
        const active = tab.dataset.category === "all";
        tab.classList.toggle("active", active);
        tab.setAttribute("aria-pressed", active ? "true" : "false");
      });
      updateTableFilters(true);
      return;
    }

    const statusChip = e.target.closest(".status-chip");
    if (statusChip) {
      document.querySelectorAll(".status-chip").forEach((c) => c.classList.toggle("active", c === statusChip));
      updateTableFilters(false);
      return;
    }

    const archChip = e.target.closest(".arch-chip");
    if (archChip) {
      document.querySelectorAll(".arch-chip").forEach((c) => c.classList.toggle("active", c === archChip));
      updateTableFilters(false);
    }
  });

  function onPageReady() {
    initFleetCatalog();
    initDeployCustomizer();
    humanizeLastCheck();
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(onPageReady);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onPageReady);
  } else {
    onPageReady();
  }
})();
