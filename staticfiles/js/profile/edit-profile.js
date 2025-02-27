document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.getElementById('edit-profile-form');
    const photoInput = document.getElementById('profile-photo');
    const currentPhoto = document.getElementById('current-photo');
    const changePhotoBtn = document.querySelector('.change-photo-btn');

    // Load existing profile data
    loadProfileData();

    // Photo upload handling
    changePhotoBtn.addEventListener('click', () => {
        photoInput.click();
    });

    photoInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                currentPhoto.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    // Form submission
    profileForm.addEventListener('submit', function(e) {
        e.preventDefault();
        saveProfileData();
    });

    function loadProfileData() {
        const userData = JSON.parse(localStorage.getItem('currentUser')) || {};
        document.getElementById('name').value = userData.name || '';
        document.getElementById('email').value = userData.email || '';
        document.getElementById('phone').value = userData.phone || '';
        if (userData.photo) {
            currentPhoto.src = userData.photo;
        }
    }

    function saveProfileData() {
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            photo: currentPhoto.src
        };

        localStorage.setItem('currentUser', JSON.stringify(formData));
        alert('Profile updated successfully!');
    }
}); 