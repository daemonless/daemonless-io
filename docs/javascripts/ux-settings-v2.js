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

// Image Search & Status Filtering
function updateTableFilters() {
    const input = document.getElementById('image-search');
    const query = input ? input.value.toLowerCase().trim() : '';
    const statusChip = document.querySelector('.status-chip.active');
    const statusFilter = statusChip ? statusChip.dataset.filter : 'all';
    const archChip = document.querySelector('.arch-chip.active');
    const archFilter = archChip ? archChip.dataset.arch : 'all';

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

            // Status filter logic
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

            // Architecture filter logic (when status is 'all')
            let archMatch = true;
            if (statusFilter === 'all' && archFilter !== 'all') {
                if (archFilter === 'amd64') archMatch = hasAmd64;
                else if (archFilter === 'arm64') archMatch = hasArm64;
            }

            // Search query logic
            const textMatch = !query || row.textContent.toLowerCase().includes(query);

            const show = statusMatch && archMatch && textMatch;
            row.style.display = show ? '' : 'none';
            if (show) matchCount++;
        });

        // Hide table and its header if no matches
        const header = table.previousElementSibling;
        const isFiltering = query !== '' || statusFilter !== 'all' || archFilter !== 'all';
        if (matchCount === 0 && isFiltering) {
            table.style.display = 'none';
            if (header && header.tagName.startsWith('H')) header.style.display = 'none';
        } else {
            table.style.display = '';
            if (header && header.tagName.startsWith('H')) header.style.display = '';
        }
    });
}

// Event Delegation for Search Input
document.addEventListener('input', e => {
    if (e.target.id === 'image-search') {
        updateTableFilters();
    }
});

// Event Delegation for Filter Chips (Status & Architecture)
document.addEventListener('click', e => {
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
