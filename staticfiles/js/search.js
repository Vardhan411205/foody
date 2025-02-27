// Common search functionality
function initializeSearch() {
    // Get the search elements
    const searchInput = document.getElementById('quickbite-search');
    const searchBtn = document.querySelector('.search-btn');
    
    // Exit if we're not on a page with search functionality
    if (!searchInput || !searchBtn) return;

    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const items = document.querySelectorAll('.product-card');
        let hasResults = false;

        items.forEach(item => {
            const title = item.querySelector('h3')?.textContent?.toLowerCase() || '';
            const category = item.querySelector('.category-tag')?.textContent?.toLowerCase() || '';
            
            if (title.includes(searchTerm) || category.includes(searchTerm)) {
                item.style.display = '';
                hasResults = true;
            } else {
                item.style.display = 'none';
            }
        });

        // Show/hide no results message if it exists
        const noResults = document.querySelector('.no-results');
        if (noResults) {
            noResults.style.display = hasResults ? 'none' : 'block';
        }
    }

    // Add event listeners
    searchInput.addEventListener('input', performSearch);
    searchBtn.addEventListener('click', (e) => {
        e.preventDefault();
        performSearch();
    });
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });
}

// Initialize search when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeSearch);

document.addEventListener('DOMContentLoaded', function() {
    // Get search input and items based on page type
    const searchInput = document.querySelector('.search-picker input');
    let searchableItems;
    let noResultsMessage;

    // Initialize based on page type
    if (document.body.classList.contains('food-page')) {
        searchableItems = document.querySelectorAll('.restaurant-card');
        initializeSearch('restaurant', ['name', 'cuisine', 'features']);
    } else if (document.body.classList.contains('buzzfest-page')) {
        searchableItems = document.querySelectorAll('.venue-card');
        initializeSearch('venue', ['name', 'type', 'features', 'capacity']);
    } else if (document.body.classList.contains('quickbite-page')) {
        searchableItems = document.querySelectorAll('.product-card');
        initializeSearch('product', ['name', 'category', 'description']);
    } else if (document.body.classList.contains('dinespot-page')) {
        searchableItems = document.querySelectorAll('.restaurant-card');
        initializeSearch('restaurant', ['name', 'cuisine', 'features']);
    }

    function initializeSearch(itemType, searchFields) {
        // Create no results message if it doesn't exist
        if (!document.querySelector('.no-results')) {
            noResultsMessage = document.createElement('div');
            noResultsMessage.className = 'no-results';
            noResultsMessage.textContent = `No ${itemType}s found matching your search`;
            noResultsMessage.style.display = 'none';
            searchableItems[0].parentElement.appendChild(noResultsMessage);
        } else {
            noResultsMessage = document.querySelector('.no-results');
        }

        // Add search event listeners
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            let hasResults = false;

            searchableItems.forEach(item => {
                const searchableText = getSearchableText(item, searchFields);
                
                if (searchableText.includes(searchTerm)) {
                    item.style.display = '';
                    hasResults = true;
                    highlightMatchingText(item, searchTerm);
                } else {
                    item.style.display = 'none';
                }
            });

            noResultsMessage.style.display = hasResults ? 'none' : 'block';
        });

        // Clear search
        searchInput.addEventListener('search', function() {
            this.value = '';
            searchableItems.forEach(item => {
                item.style.display = '';
                removeHighlights(item);
            });
            noResultsMessage.style.display = 'none';
        });
    }

    function getSearchableText(item, searchFields) {
        let text = '';
        
        searchFields.forEach(field => {
            switch (field) {
                case 'name':
                    text += item.querySelector('h3').textContent.toLowerCase() + ' ';
                    break;
                case 'cuisine':
                case 'type':
                    const typeElement = item.querySelector('p');
                    if (typeElement) text += typeElement.textContent.toLowerCase() + ' ';
                    break;
                case 'features':
                    const features = item.querySelectorAll('.features span');
                    features.forEach(feature => {
                        text += feature.textContent.toLowerCase() + ' ';
                    });
                    break;
                case 'capacity':
                    const capacityElement = item.querySelector('p:nth-of-type(2)');
                    if (capacityElement) text += capacityElement.textContent.toLowerCase() + ' ';
                    break;
                case 'category':
                    const categoryTag = item.querySelector('.category-tag');
                    if (categoryTag) text += categoryTag.textContent.toLowerCase() + ' ';
                    break;
                case 'description':
                    const description = item.querySelector('.product-info p');
                    if (description) text += description.textContent.toLowerCase() + ' ';
                    break;
            }
        });

        return text.trim();
    }

    function highlightMatchingText(item, searchTerm) {
        removeHighlights(item);
        if (!searchTerm) return;

        const textNodes = getTextNodes(item);
        textNodes.forEach(node => {
            const text = node.textContent;
            const index = text.toLowerCase().indexOf(searchTerm.toLowerCase());
            if (index >= 0) {
                const span = document.createElement('span');
                span.className = 'highlight';
                const before = text.substring(0, index);
                const match = text.substring(index, index + searchTerm.length);
                const after = text.substring(index + searchTerm.length);
                span.innerHTML = `${before}<mark>${match}</mark>${after}`;
                node.parentNode.replaceChild(span, node);
            }
        });
    }

    function removeHighlights(item) {
        const highlights = item.querySelectorAll('.highlight');
        highlights.forEach(highlight => {
            const parent = highlight.parentNode;
            parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
        });
    }

    function getTextNodes(node) {
        const textNodes = [];
        const walk = document.createTreeWalker(
            node,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        let n;
        while (n = walk.nextNode()) textNodes.push(n);
        return textNodes;
    }
});