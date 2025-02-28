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

    // Initialize add to cart functionality
    const addButtons = document.querySelectorAll('.add-btn');
    const counters = document.querySelectorAll('.counter');
    
    addButtons.forEach((btn, index) => {
        btn.addEventListener('click', function() {
            this.style.display = 'none';
            counters[index].style.display = 'flex';
            counters[index].querySelector('.count').textContent = '1';
            updateCart();
        });
    });

    counters.forEach(counter => {
        const decreaseBtn = counter.querySelector('.decrease');
        const increaseBtn = counter.querySelector('.increase');
        const countDisplay = counter.querySelector('.count');
        const addBtn = counter.parentElement.querySelector('.add-btn');

        decreaseBtn.addEventListener('click', function() {
            let count = parseInt(countDisplay.textContent);
            count--;
            if (count === 0) {
                counter.style.display = 'none';
                addBtn.style.display = 'block';
            } else {
                countDisplay.textContent = count;
            }
            updateCart();
        });

        increaseBtn.addEventListener('click', function() {
            let count = parseInt(countDisplay.textContent);
            count++;
            countDisplay.textContent = count;
            updateCart();
        });
    });

    // Initialize favorite buttons
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    favoriteButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const icon = this.querySelector('i');
            icon.classList.toggle('far');
            icon.classList.toggle('fas');
            
            // Get item data
            const itemData = JSON.parse(this.dataset.item);
            
            // Update favorites in localStorage
            updateFavorites(itemData, icon.classList.contains('fas'));
        });
    });

    // Check and update initial favorite states
    checkInitialFavorites();
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

function updateCart() {
    const counters = document.querySelectorAll('.counter');
    let totalItems = 0;

    counters.forEach(counter => {
        if (counter.style.display !== 'none') {
            totalItems += parseInt(counter.querySelector('.count').textContent);
        }
    });

    // Update cart badge
    const cartBadge = document.querySelector('.cart-badge');
    if (cartBadge) {
        cartBadge.textContent = totalItems;
        cartBadge.style.display = totalItems > 0 ? 'block' : 'none';
    }
}

function checkInitialFavorites() {
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');

    favoriteButtons.forEach(btn => {
        const itemData = JSON.parse(btn.dataset.item);
        const isFavorite = favorites.some(fav => fav.name === itemData.name);
        
        if (isFavorite) {
            const icon = btn.querySelector('i');
            icon.classList.remove('far');
            icon.classList.add('fas');
        }
    });
}