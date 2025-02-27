// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const submitBtn = this.querySelector('.auth-btn');
            const spinner = submitBtn.querySelector('.loading-spinner');

            // Basic validation
            if (!email || !password) {
                showAlert('Please fill in all fields', 'error');
                return;
            }

            try {
                // Show loading state
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                spinner.style.display = 'inline-block';

                const response = await fetch('/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password,
                        remember: document.getElementById('remember').checked
                    })
                });

                const data = await response.json();
                console.log('Login response:', data);  // Debug log

                if (data.status === 'success') {
                    showAlert('Login successful! Redirecting...', 'success');
                    // Redirect after showing success message
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 1000);
                } else {
                    showAlert(data.message || 'Login failed', 'error');
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                    spinner.style.display = 'none';
                }
            } catch (error) {
                console.error('Login error:', error);
                showAlert('An error occurred during login', 'error');
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
                spinner.style.display = 'none';
            }
        });
    }

    // Password visibility toggle
    document.querySelectorAll('.toggle-password').forEach(icon => {
        icon.addEventListener('click', function() {
            const input = this.previousElementSibling;
            if (input.type === 'password') {
                input.type = 'text';
                this.classList.remove('fa-eye-slash');
                this.classList.add('fa-eye');
            } else {
                input.type = 'password';
                this.classList.remove('fa-eye');
                this.classList.add('fa-eye-slash');
            }
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showAlert(message, type = 'error') {
    const alertDiv = document.querySelector('.alert');
    if (alertDiv) {
        alertDiv.textContent = message;
        alertDiv.className = `alert ${type}`;
        alertDiv.style.display = 'block';
        
        setTimeout(() => {
            alertDiv.style.display = 'none';
        }, 5000);
    }
}