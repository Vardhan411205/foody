document.addEventListener('DOMContentLoaded', function() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const ordersList = document.querySelector('.orders-list');

    // Filter functionality
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            button.classList.add('active');

            const filter = button.dataset.filter;
            filterOrders(filter);
        });
    });

    // Reorder functionality
    document.querySelectorAll('.reorder-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const orderCard = this.closest('.order-card');
            handleReorder(orderCard);
        });
    });

    function filterOrders(filter) {
        const orders = document.querySelectorAll('.order-card');
        orders.forEach(order => {
            if (filter === 'all') {
                order.style.display = 'block';
            } else {
                const status = order.querySelector('.order-status').textContent.toLowerCase();
                order.style.display = status === filter ? 'block' : 'none';
            }
        });
    }

    function handleReorder(orderCard) {
        // Add reorder logic here
        console.log('Reordering:', orderCard);
        alert('Reorder functionality will be implemented soon!');
    }
}); 