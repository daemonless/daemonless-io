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

// Image Search Filtering (Event Delegation)
document.addEventListener('input', e => {
    if (e.target.id !== 'image-search') return;
    const query = e.target.value.toLowerCase();

    document.querySelectorAll('.md-content table').forEach(table => {
        let matchCount = 0;
        table.querySelectorAll('tbody tr').forEach(row => {
            const matches = row.textContent.toLowerCase().includes(query);
            row.style.display = matches ? '' : 'none';
            if (matches) matchCount++;
        });

        // Hide table and its header if no matches
        const header = table.previousElementSibling;
        if (matchCount === 0 && query !== '') {
            table.style.display = 'none';
            if (header && header.tagName.startsWith('H')) header.style.display = 'none';
        } else {
            table.style.display = '';
            if (header && header.tagName.startsWith('H')) header.style.display = '';
        }
    });
});

// Status page: filter chips (All / Needs attention / Current)
document.addEventListener('click', e => {
    const chip = e.target.closest('.status-chip');
    if (!chip) return;
    document.querySelectorAll('.status-chip').forEach(c =>
        c.classList.toggle('active', c === chip));
    const filter = chip.dataset.filter;
    document.querySelectorAll('.md-content table tbody tr').forEach(row => {
        const isOutdated = !!row.querySelector('.outdated');
        const show = filter === 'all' || (filter === 'outdated') === isOutdated;
        row.style.display = show ? '' : 'none';
    });
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
