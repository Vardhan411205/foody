document.addEventListener('DOMContentLoaded', function() {
    const categoryLinks = document.querySelectorAll('.category-item a');
    const restaurantCards = document.querySelectorAll('.restaurant-card');
    const searchInput = document.querySelector('.search-picker input');
    const sectionTitle = document.querySelector('.restaurants-section h2');

    // Category filtering
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Update active state
            categoryLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            const category = this.querySelector('span').textContent;
            sectionTitle.textContent = category === 'All' ? 'All Restaurants' : `${category} Restaurants`;

            // Filter restaurants
            restaurantCards.forEach(card => {
                const cardCategory = card.querySelector('.category-tag').textContent;
                if (category === 'All') {
                    card.style.display = 'block';
                } else {
                    card.style.display = cardCategory === category.toUpperCase() ? 'block' : 'none';
                }
            });
        });
    });

    // Search functionality
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();

        restaurantCards.forEach(card => {
            const name = card.querySelector('h3').textContent.toLowerCase();
            const cuisine = card.querySelector('p').textContent.toLowerCase();
            const features = Array.from(card.querySelectorAll('.features span'))
                .map(span => span.textContent.toLowerCase())
                .join(' ');

            if (name.includes(searchTerm) ||
                cuisine.includes(searchTerm) ||
                features.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });

    // Add click event to category images
    document.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('click', function() {
            const category = this.querySelector('span').textContent.toLowerCase();
            const categoryLink = document.querySelector(`.scrolling-categories a[href="#${category}"]`);
            if (categoryLink) {
                categoryLink.click();
            }
        });
    });

    const noResultsMessage = document.createElement('div');
    noResultsMessage.className = 'no-results';
    noResultsMessage.textContent = 'No restaurants found matching your search';
    noResultsMessage.style.display = 'none';
    document.querySelector('.restaurant-grid').appendChild(noResultsMessage);

    // Filter functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    const sortSelect = document.getElementById('sort-select');

    // Filter by category
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filterValue = this.getAttribute('data-filter');

            // Toggle active state
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            restaurantCards.forEach(card => {
                if (filterValue === 'all') {
                    card.style.display = 'block';
                } else {
                    const cardType = card.getAttribute('data-category');
                    card.style.display = cardType === filterValue ? 'block' : 'none';
                }
            });
        });
    });

    // Sort functionality
    sortSelect.addEventListener('change', function() {
        const sortValue = this.value;
        const cardsArray = Array.from(restaurantCards);

        cardsArray.sort((a, b) => {
            switch (sortValue) {
                case 'rating-high':
                    return getRating(b) - getRating(a);
                case 'rating-low':
                    return getRating(a) - getRating(b);
                case 'price-high':
                    return getPrice(b) - getPrice(a);
                case 'price-low':
                    return getPrice(a) - getPrice(b);
                default:
                    return 0;
            }
        });

        const container = document.querySelector('.restaurant-grid');
        cardsArray.forEach(card => container.appendChild(card));
    });

    // Helper functions to get rating and price values
    function getRating(card) {
        return parseFloat(card.querySelector('.rating').textContent) || 0;
    }

    function getPrice(card) {
        const priceText = card.querySelector('.price-range').textContent;
        return priceText.split('₹').length - 1 || 0; // Count number of ₹ symbols
    }

    // Reset filters
    document.querySelector('.reset-filters').addEventListener('click', function() {
        // Reset search
        searchInput.value = '';

        // Reset filter buttons
        filterButtons.forEach(btn => btn.classList.remove('active'));
        document.querySelector('[data-filter="all"]').classList.add('active');

        // Reset sort select
        sortSelect.value = 'default';

        // Show all restaurants
        restaurantCards.forEach(card => card.style.display = 'block');
    });

    function bookTable(button) {
        const restaurantCard = button.closest('.restaurant-card');
        const tableData = {
            type: 'table',
            restaurant: restaurantCard.querySelector('h3').textContent,
            // Get the price from the pricing element (₹4000 for two -> 4000)
            price: restaurantCard.querySelector('.pricing').textContent.match(/₹([\d,]+)/)[1].replace(',', ''),
            image: restaurantCard.querySelector('img').src
        };
        localStorage.setItem('bookingData', JSON.stringify(tableData));
        window.location.href = '../payments/payments.html';
    }
});