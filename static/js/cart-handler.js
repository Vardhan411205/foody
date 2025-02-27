class CartHandler {
    constructor() {
        this.cart = JSON.parse(localStorage.getItem('foodCart')) || [];
        this.initializeQuantityControls();
        this.initializeCartBadges();
        this.updateCartBadge();
    }

    initializeQuantityControls() {
        const quantityControls = document.querySelectorAll('.quantity-control');
        if (!quantityControls.length) return;

        quantityControls.forEach(control => {
            const addBtn = control.querySelector('.add-btn');
            const counter = control.querySelector('.counter');
            const decreaseBtn = control.querySelector('.decrease');
            const increaseBtn = control.querySelector('.increase');
            const countSpan = control.querySelector('.count');
            const card = control.closest('.product-card');

            // Skip if any required element is missing
            if (!addBtn || !counter || !decreaseBtn || !increaseBtn || !countSpan || !card) return;

            // Initialize state for items already in cart
            const itemName = card.querySelector('h3').textContent;
            const existingItem = this.cart.find(item => item.name === itemName);
            
            if (existingItem) {
                addBtn.style.display = 'none';
                counter.style.display = 'flex';
                countSpan.textContent = existingItem.quantity;
                counter.style.zIndex = '3';
            }

            // Add button click handler
            addBtn.addEventListener('click', () => {
                addBtn.style.display = 'none';
                counter.style.display = 'flex';
                countSpan.textContent = '1';
                counter.style.zIndex = '3';

                const itemData = {
                    name: card.querySelector('h3').textContent,
                    price: parseFloat(card.querySelector('.price').textContent.replace('₹', '')),
                    category: card.querySelector('.category-tag').textContent,
                    quantity: 1,
                    type: 'quickbite'
                };

                this.addToCart(itemData);
            });

            // Decrease button click handler
            decreaseBtn.addEventListener('click', () => {
                const itemName = card.querySelector('h3').textContent;
                let count = parseInt(countSpan.textContent);
                count--;

                if (count === 0) {
                    this.removeFromCart(itemName);
                    counter.style.display = 'none';
                    addBtn.style.display = 'block';
                } else {
                    this.updateQuantity(itemName, count);
                    countSpan.textContent = count;
                }
            });

            // Increase button click handler
            increaseBtn.addEventListener('click', () => {
                const itemName = card.querySelector('h3').textContent;
                let count = parseInt(countSpan.textContent);
                count++;
                countSpan.textContent = count;
                this.updateQuantity(itemName, count);
            });
        });
    }

    addToCart(item) {
        const existingItem = this.cart.find(cartItem => cartItem.name === item.name);
        if (existingItem) {
            existingItem.quantity += item.quantity;
        } else {
            this.cart.push(item);
        }
        this.saveCart();
        this.updateCartBadge();
    }

    removeFromCart(itemName) {
        this.cart = this.cart.filter(item => item.name !== itemName);
        this.saveCart();
        this.updateCartBadge();
    }

    updateQuantity(itemName, quantity) {
        const item = this.cart.find(item => item.name === itemName);
        if (item) {
            item.quantity = quantity;
            this.saveCart();
            this.updateCartBadge();
        }
    }

    saveCart() {
        localStorage.setItem('foodCart', JSON.stringify(this.cart));
    }

    updateCartBadge() {
        const cartBadges = document.querySelectorAll('.cart-badge');
        const totalItems = this.cart.reduce((sum, item) => sum + item.quantity, 0);

        console.log('Updating cart badge:', {
            badgesFound: cartBadges.length,
            totalItems: totalItems,
            cart: this.cart
        });

        cartBadges.forEach(badge => {
            if (badge) {
                badge.textContent = totalItems;
                if (totalItems > 0) {
                    badge.style.display = 'flex';
                    badge.style.visibility = 'visible';
                } else {
                    badge.style.display = 'none';
                }
            }
        });
    }

    initializeCartBadges() {
        const totalItems = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        if (totalItems > 0) {
            this.updateCartBadge();
        }
    }
}

// Initialize cart handler when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CartHandler();
});