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