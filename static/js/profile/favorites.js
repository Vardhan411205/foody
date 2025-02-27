class FavoritesPage {
    constructor() {
        this.favoritesContainer = document.querySelector('.favorites-grid');
        this.emptyState = document.querySelector('.empty-state');
        this.favorites = JSON.parse(localStorage.getItem('favorites')) || [];

        this.initializeEventListeners();
        this.renderFavorites();
    }

    initializeEventListeners() {
        // Listen for favorites updates
        window.addEventListener('favoritesUpdated', () => {
            this.favorites = JSON.parse(localStorage.getItem('favorites')) || [];
            this.renderFavorites();
        });

        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(button => {
            button.addEventListener('click', () => {
                this.filterFavorites(button.dataset.category);
            });
        });
    }

    renderFavorites() {
        const sections = {
            food: document.querySelector('#food-section .favorites-cards'),
            quickbite: document.querySelector('#quickbite-section .favorites-cards'),
            dinespot: document.querySelector('#dinespot-section .favorites-cards')
        };

        // Clear existing items
        Object.values(sections).forEach(section => {
            if (section) section.innerHTML = '';
        });

        // Render items by type
        this.favorites.forEach(item => {
            const section = sections[item.type];
            if (section) {
                section.appendChild(this.createFavoriteCard(item));
            }
        });

        // Show/hide empty state
        this.toggleEmptyState();
    }

    createFavoriteCard(item) {
        const card = document.createElement('div');
        card.className = `favorite-card ${item.type}`;
        
        // This is the key part - we need to handle different types differently
        let content;
        if (item.type === 'buzzfest') {
            content = `
                <img src="${item.image}" alt="${item.name}">
                <div class="favorite-content">
                    <h3>${item.name}</h3>
                    <p class="type">${item.type}</p>
                    <p class="capacity">${item.capacity}</p>
                    <p class="price">${item.price}</p>
                    <div class="actions">
                        <button class="book-btn">Book Venue</button>
                        <button class="remove-btn" data-id="${item.id}">
                            <i class="fas fa-heart-broken"></i>
                        </button>
                    </div>
                </div>`;
        } else {
            content = `
                <img src="${item.image}" alt="${item.name}">
                <div class="favorite-content">
                    <h3>${item.name}</h3>
                    <p class="cuisine">${item.cuisine || item.type}</p>
                    ${item.rating ? `<div class="rating">${item.rating} ★</div>` : ''}
                    <p class="price">${item.price}</p>
                    <div class="actions">
                        <button class="${item.type === 'food' ? 'order-btn' : 'book-btn'}">
                            ${item.type === 'food' ? 'Order Now' : 'Book Now'}
                        </button>
                        <button class="remove-btn" data-id="${item.id}">
                            <i class="fas fa-heart-broken"></i>
                        </button>
                    </div>
                </div>`;
        }
        
        card.innerHTML = content;

        // Add remove handler
        card.querySelector('.remove-btn').addEventListener('click', () => {
            this.removeFavorite(item.id);
        });

        return card;
    }

    removeFavorite(itemId) {
        this.favorites = this.favorites.filter(item => item.id !== itemId);
        localStorage.setItem('favorites', JSON.stringify(this.favorites));
        this.renderFavorites();
    }

    toggleEmptyState() {
        if (this.favorites.length === 0) {
            this.emptyState.style.display = 'block';
            this.favoritesContainer.style.display = 'none';
        } else {
            this.emptyState.style.display = 'none';
            this.favoritesContainer.style.display = 'block';
        }
    }

    filterFavorites(category) {
        document.querySelectorAll('.category-section').forEach(section => {
            if (category === 'all' || section.id === `${category}-section`) {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
    }
}

// Initialize favorites page
document.addEventListener('DOMContentLoaded', () => {
    new FavoritesPage();
});