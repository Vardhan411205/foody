// Profile Management
class ProfileManager {
    constructor() {
        this.currentUser = JSON.parse(localStorage.getItem('currentUser')) || {
            name: 'Guest User',
            email: '',
            phone: '',
            addresses: [],
            orders: [],
            favorites: [],
            payments: []
        };
        
        this.initializeProfile();
        this.attachEventListeners();
    }

    initializeProfile() {
        // Update profile name
        const profileNameElements = document.querySelectorAll('.profile-header span');
        profileNameElements.forEach(element => {
            element.textContent = `Hello, ${this.currentUser.name}`;
        });
    }

    attachEventListeners() {
        // Profile menu click handlers
        document.querySelectorAll('.profile-menu li a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const action = e.currentTarget.getAttribute('href').replace('#', '');
                this.handleProfileAction(action);
            });
        });
    }

    handleProfileAction(action) {
        switch(action) {
            case 'profile':
                this.showEditProfile();
                break;
            case 'orders':
                this.showOrders();
                break;
            case 'favorites':
                this.showFavorites();
                break;
            case 'addresses':
                this.showAddresses();
                break;
            case 'payments':
                this.showPayments();
                break;
            case 'help':
                this.showHelp();
                break;
            case 'logout':
                this.handleLogout();
                break;
        }
    }

    // Profile Modal Templates
    getModalTemplate(title, content) {
        return `
            <div class="profile-modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>${title}</h3>
                        <button class="close-modal">&times;</button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                </div>
            </div>
        `;
    }

    showEditProfile() {
        const content = `
            <form id="edit-profile-form">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" name="name" value="${this.currentUser.name}" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" value="${this.currentUser.email}" required>
                </div>
                <div class="form-group">
                    <label>Phone</label>
                    <input type="tel" name="phone" value="${this.currentUser.phone}" required>
                </div>
                <button type="submit" class="save-btn">Save Changes</button>
            </form>
        `;
        this.showModal('Edit Profile', content);
        
        // Form submission handler
        document.getElementById('edit-profile-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.updateProfile(new FormData(e.target));
        });
    }

    showOrders() {
        const orders = this.currentUser.orders;
        const content = orders.length ? orders.map(order => `
            <div class="order-item">
                <h4>${order.restaurant}</h4>
                <p>Order #${order.id}</p>
                <p>Total: ₹${order.total}</p>
                <p>Status: ${order.status}</p>
            </div>
        `).join('') : '<p>No orders yet</p>';
        
        this.showModal('My Orders', content);
    }

    showFavorites() {
        const favorites = this.currentUser.favorites;
        const content = favorites.length ? favorites.map(fav => `
            <div class="favorite-item">
                <h4>${fav.name}</h4>
                <p>${fav.type}</p>
            </div>
        `).join('') : '<p>No favorites yet</p>';
        
        this.showModal('My Favorites', content);
    }

    showAddresses() {
        const addresses = this.currentUser.addresses;
        const content = `
            <div class="addresses-list">
                ${addresses.length ? addresses.map(addr => `
                    <div class="address-item">
                        <p>${addr.type}: ${addr.address}</p>
                        <button class="delete-btn" data-id="${addr.id}">Delete</button>
                    </div>
                `).join('') : '<p>No addresses saved</p>'}
            </div>
            <button class="add-btn" id="add-address">Add New Address</button>
        `;
        
        this.showModal('My Addresses', content);
    }

    showPayments() {
        const payments = this.currentUser.payments;
        const content = `
            <div class="payments-list">
                ${payments.length ? payments.map(payment => `
                    <div class="payment-item">
                        <p>${payment.type}: ****${payment.last4}</p>
                        <button class="delete-btn" data-id="${payment.id}">Delete</button>
                    </div>
                `).join('') : '<p>No payment methods saved</p>'}
            </div>
            <button class="add-btn" id="add-payment">Add Payment Method</button>
        `;
        
        this.showModal('Payment Methods', content);
    }

    showHelp() {
        const content = `
            <div class="help-content">
                <h4>Contact Support</h4>
                <p>Email: support@mrfoody.com</p>
                <p>Phone: +91 123 456 7890</p>
                <h4>FAQs</h4>
                <div class="faq-item">
                    <h5>How do I place an order?</h5>
                    <p>Select your items and proceed to checkout. Choose your delivery address and payment method.</p>
                </div>
                <div class="faq-item">
                    <h5>What are the delivery charges?</h5>
                    <p>Delivery charges vary based on distance and order value.</p>
                </div>
            </div>
        `;
        
        this.showModal('Help & Support', content);
    }

    handleLogout() {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.removeItem('currentUser');
            window.location.href = '../login/login.html';
        }
    }

    showModal(title, content) {
        // Remove existing modal if any
        const existingModal = document.querySelector('.profile-modal');
        if (existingModal) {
            existingModal.remove();
        }

        // Create and add new modal
        const modalHTML = this.getModalTemplate(title, content);
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Add event listeners
        const modal = document.querySelector('.profile-modal');
        const closeBtn = modal.querySelector('.close-modal');

        closeBtn.addEventListener('click', () => {
            modal.remove();
        });

        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    updateProfile(formData) {
        const updatedUser = {
            ...this.currentUser,
            name: formData.get('name'),
            email: formData.get('email'),
            phone: formData.get('phone')
        };

        localStorage.setItem('currentUser', JSON.stringify(updatedUser));
        this.currentUser = updatedUser;
        this.initializeProfile();
        
        // Close modal
        document.querySelector('.profile-modal').remove();
        
        // Show success message
        alert('Profile updated successfully!');
    }
}

// Initialize profile manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProfileManager();
}); 