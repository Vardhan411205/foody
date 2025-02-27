document.addEventListener('DOMContentLoaded', function() {
    const cartItemsContainer = document.querySelector('.cart-items');
    const emptyCartMessage = document.querySelector('.empty-cart');
    const itemsTotal = document.querySelector('.items-total');
    const deliveryFee = document.querySelector('.delivery-fee');
    const taxesAmount = document.querySelector('.taxes-amount');
    const totalAmount = document.querySelector('.total-amount');
    const checkoutBtn = document.querySelector('.checkout-btn');

    function loadCartItems() {
        const cartItems = JSON.parse(localStorage.getItem('foodCart')) || [];

        if (cartItems.length === 0) {
            emptyCartMessage.style.display = 'block';
            cartItemsContainer.style.display = 'none';
            checkoutBtn.disabled = true;
            return;
        }

        emptyCartMessage.style.display = 'none';
        cartItemsContainer.style.display = 'block';
        checkoutBtn.disabled = false;
        cartItemsContainer.innerHTML = '';

        // Group items by restaurant
        const groupedItems = groupByRestaurant(cartItems);

        // Display items grouped by restaurant
        Object.entries(groupedItems).forEach(([restaurant, items]) => {
            const restaurantSection = document.createElement('div');
            restaurantSection.className = 'restaurant-section';
            restaurantSection.innerHTML = `
                <div class="restaurant-header">
                    <h3>${restaurant}</h3>
                </div>
            `;

            items.forEach(item => {
                const cartItem = document.createElement('div');
                cartItem.className = 'cart-item';
                cartItem.innerHTML = `
                    <div class="item-details">
                        <h3 class="item-name">${item.name}</h3>
                        <div class="item-actions">
                            <div class="quantity-control">
                                <button class="quantity-btn decrease" onclick="updateQuantity('${item.name}', ${item.quantity - 1})">-</button>
                                <span class="quantity">${item.quantity}</span>
                                <button class="quantity-btn increase" onclick="updateQuantity('${item.name}', ${item.quantity + 1})">+</button>
                            </div>
                            <span class="item-price">₹${item.price * item.quantity}</span>
                        </div>
                    </div>
                `;
                restaurantSection.appendChild(cartItem);
            });

            cartItemsContainer.appendChild(restaurantSection);
        });

        updateSummary(cartItems);
    }

    function groupByRestaurant(items) {
        return items.reduce((groups, item) => {
            const restaurant = item.restaurant || 'Other';
            if (!groups[restaurant]) {
                groups[restaurant] = [];
            }
            groups[restaurant].push(item);
            return groups;
        }, {});
    }

    function updateSummary(items) {
        const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        // Make delivery free for orders over ₹100
        const delivery = subtotal > 100 ? 0 : 40;
        const taxes = Math.round(subtotal * 0.05); // 5% tax

        itemsTotal.textContent = `₹${subtotal}`;
        deliveryFee.textContent = `₹${delivery}${subtotal > 100 ? ' (Free)' : ''}`;
        taxesAmount.textContent = `₹${taxes}`;
        totalAmount.textContent = `₹${subtotal + delivery + taxes + 1}`; // +1 for platform fee

        // Update delivery message if needed
        const deliveryMsg = document.querySelector('.delivery-message');
        if (!deliveryMsg) {
            const summaryRow = document.querySelector('.summary-row:nth-child(2)');
            const message = document.createElement('div');
            message.className = 'delivery-message';
            summaryRow.insertAdjacentElement('afterend', message);
        }

        if (subtotal > 0 && subtotal < 100) {
            deliveryMsg.textContent = `Add items worth ₹${100 - subtotal} more for free delivery`;
            deliveryMsg.style.display = 'block';
        } else {
            deliveryMsg.style.display = 'none';
        }
    }

    // Function to update item quantity
    window.updateQuantity = function(itemName, newQuantity) {
        let foodCart = JSON.parse(localStorage.getItem('foodCart')) || [];

        if (newQuantity <= 0) {
            // Remove item
            foodCart = foodCart.filter(item => item.name !== itemName);
        } else {
            // Update quantity
            const item = foodCart.find(item => item.name === itemName);
            if (item) {
                item.quantity = newQuantity;
            }
        }

        // Save updated cart
        localStorage.setItem('foodCart', JSON.stringify(foodCart));

        // Reload cart display
        loadCartItems();
    }

    function proceedToCheckout() {
        // Navigate to payments page
        window.location.href = '../payments/payments.html';
    }

    // Initial load
    loadCartItems();
});