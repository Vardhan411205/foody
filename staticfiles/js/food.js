document.addEventListener('DOMContentLoaded', function() {
    console.log('Food.js loaded');

    // Get all category links and food cards
    const categoryLinks = document.querySelectorAll('.category-item a');
    const restaurantCards = document.querySelectorAll('.restaurant-card');
    const sectionTitle = document.querySelector('.restaurants-section h2');

    // Category filtering
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Update active state
            categoryLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            const category = this.querySelector('span').textContent;
            sectionTitle.textContent = category === 'All' ? 'All Restaurants' : `${category} Items`;

            // Filter restaurants
            restaurantCards.forEach(card => {
                const cardCategory = card.querySelector('.category-tag').textContent;
                if (category === 'All') {
                    card.style.display = 'block';
                } else {
                    card.style.display = cardCategory.toLowerCase() === category.toLowerCase() ? 'block' : 'none';
                }
            });
        });
    });

    // Add click event to category images
    document.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('click', function() {
            const link = this.querySelector('a');
            if (link) {
                link.click();
            }
        });
    });

    // Search functionality
    const searchInput = document.querySelector('.search-picker input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();

            restaurantCards.forEach(card => {
                const name = card.querySelector('h3').textContent.toLowerCase();
                const cuisine = card.querySelector('.restaurant-name').textContent.toLowerCase();
                const category = card.querySelector('.category-tag').textContent.toLowerCase();

                if (name.includes(searchTerm) ||
                    cuisine.includes(searchTerm) ||
                    category.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Initialize cart functionality
    initializeCart();
});

// Profile dropdown functionality
function toggleProfileMenu() {
    const dropdown = document.querySelector('.profile-dropdown');
    dropdown.classList.toggle('active');

    // Close dropdown when clicking outside
    document.addEventListener('click', function closeDropdown(e) {
        if (!e.target.closest('.profile-icon')) {
            dropdown.classList.remove('active');
            document.removeEventListener('click', closeDropdown);
        }
    });
}

// Close dropdown when pressing Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const dropdown = document.querySelector('.profile-dropdown');
        dropdown.classList.remove('active');
    }
});

// Add this function to show favorites notification
function showFavoriteNotification(action) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerHTML = `
        <span>${action === 'add' ? 'Added to' : 'Removed from'} favorites!</span>
        <a href="../profile/favorites.html">View Favorites</a>
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Update the favorite button click handler
document.querySelectorAll('.favorite-btn').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();

        const itemData = JSON.parse(this.dataset.item);
        const itemId = this.dataset.id;
        const isActive = this.classList.contains('active');

        if (!isActive) {
            this.classList.add('active');
            this.innerHTML = '<i class="fas fa-heart"></i>';
            addToFavorites(itemId, itemData);
            showFavoriteNotification('add');
        } else {
            this.classList.remove('active');
            this.innerHTML = '<i class="far fa-heart"></i>';
            removeFromFavorites(itemId);
            showFavoriteNotification('remove');
        }
    });
});

function safeGetCart() {
    try {
        return JSON.parse(localStorage.getItem('foodCart') || '[]');
    } catch (e) {
        console.error('Error reading cart:', e);
        return [];
    }
}

function safeSetCart(cart) {
    try {
        localStorage.setItem('foodCart', JSON.stringify(cart));
    } catch (e) {
        console.error('Error saving cart:', e);
    }
}