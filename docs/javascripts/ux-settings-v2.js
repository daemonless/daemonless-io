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
