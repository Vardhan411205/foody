// In your form submission handler
document.getElementById('signupForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // ... existing validation code ...

    try {
        const response = await fetch('/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        if (data.status === 'success') {
            showAlert('Registration successful! Redirecting to login...', 'success');
            setTimeout(() => {
                window.location.href = data.redirect_url || '/login/';
            }, 1500);
        } else {
            showAlert(data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('An error occurred during registration', 'error');
    }
}); 