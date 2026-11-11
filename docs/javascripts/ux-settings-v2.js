(function() {
    let moved = false;

    function moveTable() {
        if (moved) return;

        const tableDiv = document.querySelector(".auto-input-table");
        if (!tableDiv) return;

        // Find target header
        const targetHeader = document.getElementById("interactive-configuration");

        if (targetHeader) {
            console.log("UX Settings: Moving table AFTER", targetHeader);

            // Move Table
            if (targetHeader.nextSibling) {
                targetHeader.parentNode.insertBefore(tableDiv, targetHeader.nextSibling);
            } else {
                targetHeader.parentNode.appendChild(tableDiv);
            }

            // Ensure Visible
            tableDiv.style.display = "block";
            tableDiv.style.marginTop = "1rem";
            tableDiv.style.marginBottom = "1rem";

            // Find Reset Button logic
            // The plugin often puts it in .placeholder-settings-panel (sibling) OR inside tableDiv
            const settingsPanel = document.querySelector(".placeholder-settings-panel");

            if (settingsPanel) {
                // Move it AFTER table
                if (tableDiv.nextSibling) {
                    tableDiv.parentNode.insertBefore(settingsPanel, tableDiv.nextSibling);
                } else {
                    tableDiv.parentNode.appendChild(settingsPanel);
                }
                settingsPanel.style.display = "block";
                settingsPanel.style.marginBottom = "2rem";
            }

            moved = true;
        }
    }

    const observer = new MutationObserver((mutations) => {
        if (moved) {
            observer.disconnect();
            return;
        }
        if (document.querySelector(".auto-input-table")) {
            moveTable();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
    window.addEventListener("DOMContentLoaded", moveTable);
    window.addEventListener("load", moveTable);
})();

// Image Search, Category Tabs, View Toggle & Status Filtering
const FLEET_VIEW_STORAGE_KEY = 'daemonless-fleet-view';

function setFleetView(view) {
    const cardsView = document.getElementById('fleet-cards-view');
    const tableView = document.getElementById('fleet-table-view');
    if (!cardsView || !tableView) return;

    const isTable = view === 'table';
    cardsView.hidden = isTable;
    tableView.hidden = !isTable;

    document.querySelectorAll('.fleet-view-btn').forEach(btn => {
        const active = btn.dataset.view === (isTable ? 'table' : 'cards');
        btn.classList.toggle('active', active);
        btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    try {
        localStorage.setItem(FLEET_VIEW_STORAGE_KEY, isTable ? 'table' : 'cards');
    } catch (_) {}
}

function updateTableFilters() {
    const input = document.getElementById('image-search');
    const query = input ? input.value.toLowerCase().trim() : '';
    const statusChip = document.querySelector('.status-chip.active');
    const statusFilter = statusChip ? statusChip.dataset.filter : 'all';
    const archChip = document.querySelector('.arch-chip.active');
    const archFilter = archChip ? archChip.dataset.arch : 'all';
    const catTab = document.querySelector('.fleet-cat-tab.active');
    const categoryFilter = catTab ? catTab.dataset.category : 'all';

    // 1. Update Card View (if on /images/)
    const activeGrid = document.getElementById('fleet-active-grid');
    let activeCardMatches = 0;
    if (activeGrid) {
        activeGrid.querySelectorAll('.fleet-card').forEach(card => {
            const catMatch = categoryFilter === 'all' || card.dataset.category === categoryFilter;
            const textMatch = !query || card.textContent.toLowerCase().includes(query);
            const show = catMatch && textMatch;
            card.hidden = !show;
            if (show) activeCardMatches++;
        });
    }

    const depSection = document.getElementById('fleet-deprecated-cards-section');
    const depGrid = document.getElementById('fleet-deprecated-grid');
    let depCardMatches = 0;
    if (depGrid) {
        depGrid.querySelectorAll('.fleet-card').forEach(card => {
            const catMatch = categoryFilter === 'all' || card.dataset.category === categoryFilter;
            const textMatch = !query || card.textContent.toLowerCase().includes(query);
            const show = catMatch && textMatch;
            card.hidden = !show;
            if (show) depCardMatches++;
        });
        if (depSection) {
            depSection.hidden = depCardMatches === 0;
        }
    }

    // 2. Update Table View (both /images/ and /status/)
    document.querySelectorAll('.md-content table').forEach(table => {
        let matchCount = 0;
        table.querySelectorAll('tbody tr').forEach(row => {
            const meta = row.querySelector('.row-meta');
            const hasMeta = !!meta;
            const isOutdated = hasMeta ? meta.classList.contains('status-outdated') : !!row.querySelector('.outdated');
            const hasAmd64 = hasMeta ? meta.classList.contains('has-amd64') : true;
            const hasArm64 = hasMeta ? meta.classList.contains('has-arm64') : true;
            const outdatedAmd64 = hasMeta ? meta.classList.contains('outdated-amd64') : isOutdated;
            const outdatedArm64 = hasMeta ? meta.classList.contains('outdated-arm64') : isOutdated;

            // Status filter logic (/status/ page)
            let statusMatch = true;
            if (statusFilter === 'outdated') {
                if (archFilter === 'amd64') statusMatch = outdatedAmd64;
                else if (archFilter === 'arm64') statusMatch = outdatedArm64;
                else statusMatch = isOutdated;
            } else if (statusFilter === 'current') {
                if (archFilter === 'amd64') statusMatch = hasAmd64 && !outdatedAmd64;
                else if (archFilter === 'arm64') statusMatch = hasArm64 && !outdatedArm64;
                else statusMatch = !isOutdated;
            }

            // Architecture filter logic (/status/ page)
            let archMatch = true;
            if (statusFilter === 'all' && archFilter !== 'all') {
                if (archFilter === 'amd64') archMatch = hasAmd64;
                else if (archFilter === 'arm64') archMatch = hasArm64;
            }

            // Category filter logic (/images/ page table: column 2 is Category)
            let catMatch = true;
            if (catTab && categoryFilter !== 'all') {
                const catCell = row.cells && row.cells.length > 2 ? row.cells[2].textContent.trim() : '';
                catMatch = catCell === categoryFilter;
            }

            // Search query logic
            const textMatch = !query || row.textContent.toLowerCase().includes(query);

            const show = statusMatch && archMatch && catMatch && textMatch;
            row.style.display = show ? '' : 'none';
            if (show) matchCount++;
        });

        // Hide table and its preceding heading/paragraph if no matches
        const header = table.previousElementSibling;
        const isFiltering = query !== '' || statusFilter !== 'all' || archFilter !== 'all' || categoryFilter !== 'all';
        if (matchCount === 0 && isFiltering) {
            table.style.display = 'none';
            if (header && (header.tagName.startsWith('H') || header.tagName === 'P')) {
                header.style.display = 'none';
                const prev = header.previousElementSibling;
                if (prev && prev.tagName.startsWith('H')) prev.style.display = 'none';
            }
        } else {
            table.style.display = '';
            if (header && (header.tagName.startsWith('H') || header.tagName === 'P')) {
                header.style.display = '';
                const prev = header.previousElementSibling;
                if (prev && prev.tagName.startsWith('H')) prev.style.display = '';
            }
        }
    });

    // 3. Update Fleet Toolbar Heading, Subtitle Count & Empty State (on /images/)
    const headingEl = document.getElementById('fleet-heading');
    const countEl = document.getElementById('fleet-count');
    const emptyEl = document.getElementById('fleet-empty-state');
    if (headingEl && countEl && activeGrid) {
        const total = parseInt(countEl.dataset.total || '0', 10);
        headingEl.textContent = categoryFilter === 'all' ? 'All Apps' : categoryFilter;
        if (query || categoryFilter !== 'all') {
            countEl.textContent = `Showing ${activeCardMatches} of ${total} native FreeBSD OCI images`;
        } else {
            countEl.textContent = `${total} native FreeBSD OCI images`;
        }
        if (emptyEl) {
            emptyEl.hidden = (activeCardMatches + depCardMatches) > 0;
        }
    }
}

function initFleetCatalog() {
    const cardsView = document.getElementById('fleet-cards-view');
    if (!cardsView) return;

    let savedView = 'cards';
    try {
        savedView = localStorage.getItem(FLEET_VIEW_STORAGE_KEY) || 'cards';
    } catch (_) {}
    setFleetView(savedView === 'table' ? 'table' : 'cards');
    updateTableFilters();
}

window.addEventListener('DOMContentLoaded', initFleetCatalog);

// Event Delegation for Search Input
document.addEventListener('input', e => {
    if (e.target.id === 'image-search') {
        updateTableFilters();
    }
});

// Event Delegation for Filter Chips, Category Tabs, View Toggle & Reset
document.addEventListener('click', e => {
    const viewBtn = e.target.closest('.fleet-view-btn');
    if (viewBtn) {
        setFleetView(viewBtn.dataset.view);
        return;
    }

    const catTab = e.target.closest('.fleet-cat-tab');
    if (catTab) {
        document.querySelectorAll('.fleet-cat-tab').forEach(tab => {
            const active = tab === catTab;
            tab.classList.toggle('active', active);
            tab.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
        updateTableFilters();
        return;
    }

    const resetBtn = e.target.closest('#fleet-reset-filters');
    if (resetBtn) {
        const input = document.getElementById('image-search');
        if (input) input.value = '';
        document.querySelectorAll('.fleet-cat-tab').forEach(tab => {
            const active = tab.dataset.category === 'all';
            tab.classList.toggle('active', active);
            tab.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
        updateTableFilters();
        return;
    }

    const statusChip = e.target.closest('.status-chip');
    if (statusChip) {
        document.querySelectorAll('.status-chip').forEach(c =>
            c.classList.toggle('active', c === statusChip));
        updateTableFilters();
        return;
    }

    const archChip = e.target.closest('.arch-chip');
    if (archChip) {
        document.querySelectorAll('.arch-chip').forEach(c =>
            c.classList.toggle('active', c === archChip));
        updateTableFilters();
        return;
    }
});

// Status page: humanize the "last checked" timestamp
(function () {
    function humanizeLastCheck() {
        const el = document.getElementById('last-check');
        if (!el || el.dataset.humanized) return;
        const then = new Date(el.getAttribute('datetime'));
        if (isNaN(then)) return;
        const mins = Math.round((Date.now() - then.getTime()) / 60000);
        let rel;
        if (mins < 1) rel = 'just now';
        else if (mins < 60) rel = mins + ' min ago';
        else if (mins < 1440) rel = Math.round(mins / 60) + ' h ago';
        else rel = Math.round(mins / 1440) + ' d ago';
        el.dataset.humanized = '1';
        el.textContent = rel + ' (' + el.textContent.trim() + ')';
    }
    // Material instant navigation swaps page content without a full load,
    // so run on both initial load and subsequent DOM mutations.
    new MutationObserver(humanizeLastCheck)
        .observe(document.body, { childList: true, subtree: true });
    window.addEventListener('DOMContentLoaded', humanizeLastCheck);
})();
