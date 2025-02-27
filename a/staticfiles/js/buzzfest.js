document.addEventListener('DOMContentLoaded', function() {
    const venueCards = document.querySelectorAll('.venue-card');

    // Search functionality
    const searchInput = document.querySelector('#venue-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();

            venueCards.forEach(card => {
                const name = card.querySelector('h3').textContent.toLowerCase();
                const type = card.querySelector('.category-tag').textContent.toLowerCase();
                const info = card.querySelector('.venue-info p').textContent.toLowerCase();
                const features = Array.from(card.querySelectorAll('.features span'))
                    .map(span => span.textContent.toLowerCase())
                    .join(' ');

                if (name.includes(searchTerm) ||
                    type.includes(searchTerm) ||
                    info.includes(searchTerm) ||
                    features.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

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

            venueCards.forEach(card => {
                if (filterValue === 'all') {
                    card.style.display = 'block';
                } else {
                    const boxType = card.getAttribute('data-category');
                    card.style.display = boxType === filterValue ? 'block' : 'none';
                }
            });
        });
    });

    // Sort functionality
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const sortValue = this.value;
            const cardsArray = Array.from(venueCards);

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

            const container = document.querySelector('.venue-grid');
            cardsArray.forEach(card => container.appendChild(card));
        });
    }

    // Helper functions
    function getRating(card) {
        return parseFloat(card.querySelector('.rating').textContent) || 0;
    }

    function getPrice(card) {
        const priceText = card.querySelector('.price-range').textContent;
        return priceText.split('₹').length - 1 || 0;
    }

    // Reset filters
    const resetButton = document.querySelector('.reset-filters');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            // Reset search
            searchInput.value = '';

            // Reset filter buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelector('[data-filter="all"]')?.classList.add('active');

            // Reset sort select
            if (sortSelect) sortSelect.value = 'default';

            // Show all venues
            venueCards.forEach(card => card.style.display = 'block');
        });
    }

    // Handle venue booking
    const bookButtons = document.querySelectorAll('.book-btn');
    bookButtons.forEach(button => {
        button.addEventListener('click', function() {
            const venueCard = this.closest('.venue-card');
            const venueData = {
                type: 'venue',
                name: venueCard.querySelector('h3').textContent,
                price: venueCard.querySelector('.pricing').textContent.match(/₹([\d,]+)/)[1].replace(',', ''),
                image: venueCard.querySelector('img').src
            };
            
            // Save to localStorage
            localStorage.setItem('bookingData', JSON.stringify(venueData));
            // Redirect to payments page
            window.location.href = '../payments/payments.html';
        });
    });
});