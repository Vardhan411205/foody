document.addEventListener('DOMContentLoaded', function() {
    initializePayments();
});

function initializePayments() {
    setupProfileDropdown();
    loadBookingData();
    setupPaymentMethodToggle();
    setupUPIVerification();
    setupOTPHandling();
}

function setupProfileDropdown() {
    const profileIcon = document.querySelector('.profile-icon');
    const dropdown = document.querySelector('.profile-dropdown');

    profileIcon.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdown.classList.toggle('show');
    });

    document.addEventListener('click', function(e) {
        if (!profileIcon.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
}

function loadBookingData() {
    const bookingData = JSON.parse(localStorage.getItem('bookingData') || '{}');
    const totalAmount = document.querySelector('.amount');
    const payAmount = document.querySelector('.pay-amount');
    
    let amount = 0;
    if (bookingData.type === 'venue') {
        amount = bookingData.price;
    } else if (bookingData.type === 'cart') {
        amount = bookingData.total;
    } else if (bookingData.type === 'table') {
        amount = bookingData.price;
    }

    totalAmount.textContent = `₹${amount}`;
    if (payAmount) {
        payAmount.textContent = amount;
    }
}

function setupPaymentMethodToggle() {
    document.querySelectorAll('input[name="payment"]').forEach(radio => {
        radio.addEventListener('change', function() {
            document.querySelectorAll('.payment-section').forEach(section => {
                section.style.display = 'none';
            });
            
            const selectedSection = document.querySelector(`.${this.value}-section`);
            if (selectedSection) {
                selectedSection.style.display = 'block';
            }
        });
    });
}

function handlePayment(e) {
    // Prevent any default behavior
    if (e) e.preventDefault();
    
    console.log('Payment handler triggered'); // Debug log
    
    const paymentMethod = document.querySelector('input[name="payment"]:checked').value;
    console.log('Payment method:', paymentMethod); // Debug log
    
    // Validate payment details
    if (!validatePaymentDetails(paymentMethod)) {
        return;
    }

    // Show OTP modal
    const otpModal = document.querySelector('.otp-modal');
    if (otpModal) {
        otpModal.style.display = 'flex';
        startOtpTimer();
        setupOtpInputs();
    } else {
        console.error('OTP modal not found'); // Debug log
    }
}

function validatePaymentDetails(paymentMethod) {
    if (paymentMethod === 'upi') {
        const upiId = document.querySelector('.upi-input').value;
        if (!upiId || !upiId.includes('@')) {
            alert('Please enter a valid UPI ID');
            return false;
        }
    } else if (paymentMethod === 'card') {
        const cardNumber = document.querySelector('.card-number').value;
        const cardExpiry = document.querySelector('.card-expiry').value;
        const cardCvv = document.querySelector('.card-cvv').value;
        const cardName = document.querySelector('.card-name input').value;
        
        if (!cardNumber || !cardExpiry || !cardCvv || !cardName) {
            alert('Please fill in all card details');
            return false;
        }
    }
    return true;
}

function setupUPIVerification() {
    const verifyBtn = document.querySelector('.verify-btn');
    if (verifyBtn) {
        verifyBtn.addEventListener('click', function() {
            const upiId = document.querySelector('.upi-input').value;
            if (upiId.includes('@')) {
                alert('UPI ID verified successfully!');
            } else {
                alert('Please enter a valid UPI ID');
            }
        });
    }
}

function setupOTPHandling() {
    // Close OTP modal
    document.querySelector('.close-otp').addEventListener('click', function() {
        document.querySelector('.otp-modal').style.display = 'none';
    });

    // Verify OTP button
    document.querySelector('.verify-otp-btn').addEventListener('click', function() {
        const inputs = document.querySelectorAll('.otp-digit');
        const otp = Array.from(inputs).map(input => input.value).join('');
        
        if (otp === '1234') { // Demo OTP
            document.querySelector('.otp-modal').style.display = 'none';
            showSuccessModal();
        } else {
            alert('Invalid OTP. Please try again.');
            inputs.forEach(input => input.value = '');
            inputs[0].focus();
        }
    });
}

function startOtpTimer() {
    let timeLeft = 300; // 5 minutes
    const timerElement = document.querySelector('.timer');
    const timer = setInterval(() => {
        timeLeft--;
        timerElement.textContent = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(timer);
            timerElement.parentElement.innerHTML = '<a href="#" class="resend-otp">Resend OTP</a>';
        }
    }, 1000);
}

function setupOtpInputs() {
    const inputs = document.querySelectorAll('.otp-digit');
    inputs.forEach((input, index) => {
        input.value = '';
        
        input.addEventListener('keyup', function(e) {
            if (e.key >= 0 && e.key <= 9) {
                if (index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }
            } else if (e.key === 'Backspace') {
                if (index > 0) {
                    inputs[index - 1].focus();
                }
            }
        });
    });
    inputs[0].focus();
}

function showSuccessModal() {
    const successModal = document.querySelector('.success-modal');
    successModal.style.display = 'flex';
    
    const transactionId = 'TXN' + Math.random().toString(36).substr(2, 9).toUpperCase();
    document.getElementById('transactionId').textContent = transactionId;
    
    const amount = document.querySelector('.amount').textContent.replace('₹', '');
    document.getElementById('amountPaid').textContent = amount;
    
    document.querySelector('.continue-btn').addEventListener('click', function() {
        generateOrderPDF();
        // Clear storage after download
        localStorage.removeItem('bookingData');
        const bookingData = JSON.parse(localStorage.getItem('bookingData') || '{}');
        if (bookingData.type === 'cart') {
            localStorage.removeItem('foodCart');
        }
        // Add a slight delay before redirecting
        setTimeout(() => {
            window.location.href = '../home/index.html';
        }, 1000);
    });
}

function generateOrderPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const bookingData = JSON.parse(localStorage.getItem('bookingData') || '{}');
    const transactionId = document.getElementById('transactionId').textContent;
    const amount = document.getElementById('amountPaid').textContent;
    const paymentMethod = document.querySelector('input[name="payment"]:checked').value.toUpperCase();
    const date = new Date().toLocaleString();

    // Add logo
    // doc.addImage('../../static/img/logocopy.png', 'PNG', 10, 10, 30, 30);

    // Add title
    doc.setFontSize(20);
    doc.text('Order Confirmation', 105, 20, { align: 'center' });

    // Add order details
    doc.setFontSize(12);
    doc.text([
        `Transaction ID: ${transactionId}`,
        `Date: ${date}`,
        `Payment Method: ${paymentMethod}`,
        `Amount Paid: ₹${amount}`,
        `Order Type: ${bookingData.type?.toUpperCase() || 'N/A'}`
    ], 20, 40);

    // Add item details based on booking type
    let yPos = 90;
    if (bookingData.type === 'cart') {
        const cartItems = JSON.parse(localStorage.getItem('foodCart') || '[]');
        doc.text('Order Items:', 20, 80);
        
        const tableData = cartItems.map(item => [
            item.name,
            item.quantity,
            `₹${item.price}`,
            `₹${item.price * item.quantity}`
        ]);

        doc.autoTable({
            startY: yPos,
            head: [['Item', 'Quantity', 'Price', 'Total']],
            body: tableData,
            theme: 'grid'
        });
    } else if (bookingData.type === 'venue') {
        doc.text([
            'Venue Details:',
            `Venue Name: ${bookingData.name}`,
            `Price: ₹${bookingData.price}`
        ], 20, 80);
    } else if (bookingData.type === 'table') {
        doc.text([
            'Restaurant Details:',
            `Restaurant Name: ${bookingData.restaurant}`,
            `Price: ₹${bookingData.price}`
        ], 20, 80);
    }

    // Add footer
    doc.setFontSize(10);
    doc.text('Thank you for your order!', 105, 280, { align: 'center' });
    doc.text('Mr.Foody & Ms.Foody', 105, 285, { align: 'center' });

    // Save the PDF
    doc.save(`order_${transactionId}.pdf`);
}

// Also update the form to prevent default submission
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.payment-methods');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
        });
    }
});