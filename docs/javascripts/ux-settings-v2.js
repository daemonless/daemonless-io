(function() {
    let moved = false;

    function moveTable() {
        if (moved) return;

        const tableDiv = document.querySelector(".auto-input-table");
        if (!tableDiv) return;

        // Find target header
        const targetHeader = document.querySelector("h3#interactive-configuration");

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

// AppJail Bundle Download
(function () {
    function getCodeBlocks(block) {
        const result = [];
        const children = Array.from(block.querySelectorAll('p, .highlight'));
        let pendingFilename = null;
        for (const el of children) {
            if (el.tagName === 'P') {
                const strong = el.querySelector('strong');
                if (strong) {
                    pendingFilename = strong.textContent.replace(':', '').trim() || null;
                }
            } else if (el.classList.contains('highlight') && pendingFilename) {
                const code = el.querySelector('code');
                if (code) result.push({ filename: pendingFilename, code: code.textContent });
                pendingFilename = null;
            }
        }
        return result;
    }

    function findImageName() {
        const h1 = document.querySelector('h1');
        return h1 ? h1.textContent.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') : '';
    }

    function injectButton(block, imageName) {
        if (block.dataset.appjailBtn) return;
        block.dataset.appjailBtn = '1';

        const btn = document.createElement('button');
        btn.className = 'md-button';
        btn.style.marginBottom = '1rem';
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;margin-right:6px"><g fill="currentColor"><rect x="40" y="40" width="205" height="205" rx="15"/><rect x="267" y="40" width="205" height="205" rx="15"/><rect x="40" y="267" width="205" height="205" rx="15"/><rect x="267" y="267" width="205" height="205" rx="15"/></g></svg>Download AppJail Bundle (.zip)';

        btn.addEventListener('click', async function () {
            const files = getCodeBlocks(block);
            if (!files.length || typeof JSZip === 'undefined') return;
            const zip = new JSZip();
            files.forEach(f => zip.file(f.filename, f.code));
            const blob = await zip.generateAsync({ type: 'blob' });
            const a = Object.assign(document.createElement('a'), {
                href: URL.createObjectURL(blob),
                download: (imageName ? imageName + '-' : '') + 'appjail.zip',
            });
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(a.href);
        });

        block.appendChild(btn);
    }

    function processAppJailTabs() {
        const imageName = findImageName();
        document.querySelectorAll('.tabbed-set').forEach(function (set) {
            const labels = set.querySelectorAll('.tabbed-labels label');
            const blocks = set.querySelectorAll('.tabbed-content .tabbed-block');
            labels.forEach(function (label, i) {
                if (label.textContent.includes('AppJail') && blocks[i]) {
                    injectButton(blocks[i], imageName);
                }
            });
        });
    }

    window.addEventListener('load', processAppJailTabs);
    document.addEventListener('DOMContentSwitch', processAppJailTabs);
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
