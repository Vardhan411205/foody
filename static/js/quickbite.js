document.addEventListener('DOMContentLoaded', function() {
    const cartHandler = new CartHandler();

    // Get all category links and product cards
    const categoryLinks = document.querySelectorAll('.scrolling-categories a');
    const allProductCards = document.querySelectorAll('.product-card');
    const sectionTitle = document.querySelector('.products-section h2');

    // Function to update products display
    function filterProducts(category) {
        allProductCards.forEach(card => {
            if (category === 'all') {
                card.style.display = 'block';
                sectionTitle.textContent = 'All Products';
            } else {
                // Handle 'fruits' category which includes 'Fruits & Veggies'
                if (category === 'fruits' && card.classList.contains('fruits')) {
                    card.style.display = 'block';
                } else if (card.classList.contains(category)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }

                // Update section title based on category
                switch (category) {
                    case 'fruits':
                        sectionTitle.textContent = 'Fruits & Vegetables';
                        break;
                    case 'dairy':
                        sectionTitle.textContent = 'Dairy Products';
                        break;
                    case 'beverages':
                        sectionTitle.textContent = 'Beverages';
                        break;
                    case 'staples':
                        sectionTitle.textContent = 'Staples';
                        break;
                    case 'household':
                        sectionTitle.textContent = 'Household Items';
                        break;
                    case 'personal':
                        sectionTitle.textContent = 'Personal Care';
                        break;
                    default:
                        sectionTitle.textContent = `${category.charAt(0).toUpperCase() + category.slice(1)} Products`;
                }
            }
        });
    }

    // Add click event to each category link
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Remove active class from all links
            categoryLinks.forEach(l => l.classList.remove('active'));
            // Add active class to clicked link
            this.classList.add('active');

            // Get category from href attribute and filter
            const category = this.getAttribute('href').replace('#', '');
            filterProducts(category);
        });
    });

    // Add click event to category images (optional, if you want the images to be clickable too)
    document.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('click', function() {
            const link = this.querySelector('a');
            if (link) {
                link.click();
            }
        });
    });

    // Add quantity control functionality
    const quantityControls = document.querySelectorAll('.quantity-control');

    quantityControls.forEach(control => {
        const addBtn = control.querySelector('.add-btn');
        const counter = control.querySelector('.counter');
        const decreaseBtn = control.querySelector('.decrease');
        const increaseBtn = control.querySelector('.increase');
        const countSpan = control.querySelector('.count');
        const card = control.closest('.product-card');

        addBtn.addEventListener('click', () => {
            addBtn.style.display = 'none';
            counter.style.display = 'flex';
            countSpan.textContent = '1';
            
            // Add item to cart
            const itemData = {
                name: card.querySelector('h3').textContent,
                price: parseFloat(card.querySelector('.price').textContent.replace('₹', '')),
                category: card.querySelector('.category-tag').textContent,
                quantity: 1,
                type: 'quickbite'
            };
            
            cartHandler.addToCart(itemData);
        });

        decreaseBtn.addEventListener('click', () => {
            let count = parseInt(countSpan.textContent);
            if (count > 1) {
                countSpan.textContent = count - 1;
                cartHandler.updateQuantity(card.querySelector('h3').textContent, count - 1);
            } else {
                counter.style.display = 'none';
                addBtn.style.display = 'block';
                cartHandler.removeFromCart(card.querySelector('h3').textContent);
            }
        });

        increaseBtn.addEventListener('click', () => {
            let count = parseInt(countSpan.textContent);
            countSpan.textContent = count + 1;
            cartHandler.updateQuantity(card.querySelector('h3').textContent, count + 1);
        });
    });

    // Initialize cart items on page load
    function initializeCartItems() {
        const cart = cartHandler.cart;
        cart.forEach(item => {
            const productCards = document.querySelectorAll('.product-card');
            productCards.forEach(card => {
                if (card.querySelector('h3').textContent === item.name) {
                    const addBtn = card.querySelector('.add-btn');
                    const counter = card.querySelector('.counter');
                    const countSpan = card.querySelector('.count');
                    
                    addBtn.style.display = 'none';
                    counter.style.display = 'flex';
                    countSpan.textContent = item.quantity;
                }
            });
        });
        cartHandler.updateCartBadge();
    }

    // Initialize cart on page load
    initializeCartItems();
});