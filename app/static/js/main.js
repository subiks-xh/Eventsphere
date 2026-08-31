// EventSphere - Main JavaScript

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Confirm before form submission
function confirmSubmit(message) {
    return confirm(message || 'Are you sure you want to submit this form?');
}

// Mark notification as read when clicked
document.addEventListener('DOMContentLoaded', function() {
    const notificationLinks = document.querySelectorAll('.notification-item');
    notificationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const notificationId = this.dataset.notificationId;
            fetch(`/notifications/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            }).then(response => {
                if (response.ok) {
                    this.classList.remove('active');
                }
            });
        });
    });
});

// Get CSRF token from meta tag or cookie
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    
    // Try to get from cookie
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    
    return cookieValue;
}

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });
});

// Toggle password visibility
document.addEventListener('DOMContentLoaded', function() {
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const passwordInput = document.getElementById(targetId);
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Toggle icon
            const icon = this.querySelector('i');
            if (type === 'text') {
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            } else {
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
        });
    });
});

// QR Code Scanner (if supported)
function scanQRCode() {
    if ('BarcodeDetector' in window) {
        // Use Barcode Detection API
        navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
            .then(stream => {
                const barcodeDetector = new BarcodeDetector({ formats: ['qr_code'] });
                const video = document.createElement('video');
                video.srcObject = stream;
                video.play();
                
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                
                function scan() {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    context.drawImage(video, 0, 0, canvas.width, canvas.height);
                    
                    barcodeDetector.detect(canvas)
                        .then(barcodes => {
                            if (barcodes.length > 0) {
                                const qrData = barcodes[0].rawValue;
                                // Handle QR data (e.g., redirect or fill form)
                                console.log('QR Code detected:', qrData);
                                
                                // Stop scanning
                                stream.getTracks().forEach(track => track.stop());
                                
                                // You can redirect or process the QR data here
                                // For example, fill a ticket ID field:
                                const ticketInput = document.getElementById('ticket_id');
                                if (ticketInput) {
                                    ticketInput.value = qrData;
                                    ticketInput.dispatchEvent(new Event('change'));
                                }
                            } else {
                                requestAnimationFrame(scan);
                            }
                        })
                        .catch(err => {
                            console.error('Error detecting barcode:', err);
                            requestAnimationFrame(scan);
                        });
                }
                
                requestAnimationFrame(scan);
            })
            .catch(err => {
                console.error('Error accessing camera:', err);
                alert('Could not access camera. Please check permissions.');
            });
    } else {
        alert('QR code scanning is not supported in your browser.');
    }
}

// Simple countdown timer for event deadlines
function startCountdown(elementId, deadline) {
    const countdownElement = document.getElementById(elementId);
    if (!countdownElement) return;
    
    function updateCountdown() {
        const now = new Date().getTime();
        const distance = deadline - now;
        
        if (distance < 0) {
            countdownElement.innerHTML = 'Registration closed';
            return;
        }
        
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        countdownElement.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
    }
    
    updateCountdown();
    setInterval(updateCountdown, 1000);
}

// Initialize countdowns on page load
document.addEventListener('DOMContentLoaded', function() {
    const countdownElements = document.querySelectorAll('[data-countdown]');
    countdownElements.forEach(element => {
        const deadline = new Date(element.dataset.countdown).getTime();
        startCountdown(element.id, deadline);
    });
});

// Format date for display
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Format time for display
function formatTime(timeString) {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    return `${hour12}:${minutes} ${ampm}`;
}

// Copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show success message
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    Copied to clipboard!
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        document.body.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 2000 });
        bsToast.show();
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
}

// Validate form before submission
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    // Add custom validation logic here if needed
    return true;
}

// Show loading spinner
function showLoading(element) {
    const spinner = document.createElement('span');
    spinner.className = 'spinner-border spinner-border-sm';
    spinner.setAttribute('role', 'status');
    spinner.innerHTML = '<span class="visually-hidden">Loading...</span>';
    
    element.disabled = true;
    element.innerHTML = '';
    element.appendChild(spinner);
    element.appendChild(document.createTextNode(' Loading...'));
}

// Hide loading spinner
function hideLoading(element, originalText) {
    element.disabled = false;
    element.innerHTML = originalText;
}

// Submit form with loading state
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[data-loading]');
    forms.forEach(form => {
        const submitButton = form.querySelector('[type="submit"]');
        if (submitButton) {
            const originalText = submitButton.innerHTML;
            form.addEventListener('submit', function() {
                showLoading(submitButton, originalText);
            });
        }
    });
});
