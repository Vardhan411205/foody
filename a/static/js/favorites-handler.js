class FavoritesHandler {
    constructor() {
        this.favorites = JSON.parse(localStorage.getItem('favorites')) || [];
        this.initializeFavoriteButtons();
    }

    initializeFavoriteButtons() {
        const favoriteButtons = document.querySelectorAll('.favorite-btn');
        favoriteButtons.forEach(button => {
            // Check if already favorited
            const itemId = button.dataset.id;
            if (this.isItemFavorite(itemId)) {
                button.classList.add('active');
                button.innerHTML = '<i class="fas fa-heart"></i>';
            }

            // Add click handler
            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleFavorite(button);
            });
        });
    }

    toggleFavorite(button) {
        const itemId = button.dataset.id;
        const itemData = JSON.parse(button.dataset.item);
        const itemType = button.dataset.type;

        if (this.isItemFavorite(itemId)) {
            this.removeFavorite(itemId);
            button.classList.remove('active');
            button.innerHTML = '<i class="far fa-heart"></i>';
            this.showNotification('remove');
        } else {
            this.addFavorite({
                id: itemId,
                type: itemType,
                ...itemData
            });
            button.classList.add('active');
            button.innerHTML = '<i class="fas fa-heart"></i>';
            this.showNotification('add');
        }
    }

    addFavorite(item) {
        if (!this.isItemFavorite(item.id)) {
            this.favorites.push(item);
            this.saveFavorites();
        }
    }

    removeFavorite(itemId) {
        this.favorites = this.favorites.filter(item => item.id !== itemId);
        this.saveFavorites();
    }

    isItemFavorite(itemId) {
        return this.favorites.some(item => item.id === itemId);
    }

    saveFavorites() {
        localStorage.setItem('favorites', JSON.stringify(this.favorites));
        // Dispatch event for favorites page to update
        window.dispatchEvent(new CustomEvent('favoritesUpdated'));
    }

    showNotification(action) {
        const notification = document.createElement('div');
        notification.className = 'cart-notification';
        notification.innerHTML = `
            <div class="message-content">
                <i class="fas fa-heart"></i>
                <span>${action === 'add' ? 'Added to' : 'Removed from'} favorites!</span>
                <a href="/profile/favorites/" class="go-to-cart">View Favorites</a>
            </div>
        `;
        document.body.appendChild(notification);
        
        // Add show class after a small delay for animation
        setTimeout(() => notification.classList.add('show'), 100);

        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Initialize favorites handler
document.addEventListener('DOMContentLoaded', () => {
    new FavoritesHandler();
});