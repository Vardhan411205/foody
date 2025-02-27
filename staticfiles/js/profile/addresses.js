document.addEventListener('DOMContentLoaded', function() {
    const addAddressBtn = document.getElementById('add-address-btn');
    const addressModal = document.getElementById('address-modal');
    const addressForm = document.getElementById('address-form');

    // Open modal
    addAddressBtn.addEventListener('click', () => {
        showAddressModal();
    });

    // Close modal
    document.querySelector('.close-modal').addEventListener('click', () => {
        hideAddressModal();
    });

    // Form submission
    addressForm.addEventListener('submit', function(e) {
        e.preventDefault();
        saveAddress();
    });

    // Delete address
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this address?')) {
                this.closest('.address-card').remove();
            }
        });
    });

    // Edit address
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const addressCard = this.closest('.address-card');
            editAddress(addressCard);
        });
    });

    function showAddressModal(isEdit = false) {
        addressModal.style.display = 'block';
        document.querySelector('.modal-header h2').textContent = 
            isEdit ? 'Edit Address' : 'Add New Address';
    }

    function hideAddressModal() {
        addressModal.style.display = 'none';
        addressForm.reset();
    }

    function saveAddress() {
        // Add address saving logic here
        hideAddressModal();
        alert('Address saved successfully!');
    }

    function editAddress(addressCard) {
        // Populate form with existing address details
        showAddressModal(true);
        // Add logic to populate form fields
    }
}); 