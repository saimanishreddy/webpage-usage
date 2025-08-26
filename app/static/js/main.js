/**
 * Main JavaScript file for form interactions and user experience enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Form validation and enhancement
    const form = document.querySelector('.submission-form');
    if (form) {
        initializeFormValidation(form);
        initializeFormEnhancements(form);
    }

    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });

    // Add loading state to form submission
    if (form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Submitting...';
                submitBtn.disabled = true;
            }
        });
    }
});

function initializeFormValidation(form) {
    const nameInput = form.querySelector('#name');
    const emailInput = form.querySelector('#email');
    const messageInput = form.querySelector('#message');

    // Real-time validation
    if (nameInput) {
        nameInput.addEventListener('blur', function() {
            validateName(this);
        });
    }

    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            validateEmail(this);
        });
    }

    if (messageInput) {
        messageInput.addEventListener('input', function() {
            validateMessageLength(this);
        });
    }
}

function initializeFormEnhancements(form) {
    // Character counter for message field
    const messageInput = form.querySelector('#message');
    if (messageInput) {
        const charCounter = document.createElement('div');
        charCounter.className = 'char-counter';
        charCounter.textContent = '0 / 1000 characters';
        messageInput.parentNode.appendChild(charCounter);

        messageInput.addEventListener('input', function() {
            const length = this.value.length;
            charCounter.textContent = `${length} / 1000 characters`;
            charCounter.className = length > 1000 ? 'char-counter error' : 'char-counter';
        });
    }

    // Form reset confirmation
    const resetBtn = form.querySelector('button[type="reset"]');
    if (resetBtn) {
        resetBtn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to clear all form data?')) {
                e.preventDefault();
            }
        });
    }
}

function validateName(input) {
    const value = input.value.trim();
    const errorElement = getOrCreateErrorElement(input);

    if (!value) {
        showFieldError(input, errorElement, 'Name is required.');
        return false;
    } else if (value.length > 100) {
        showFieldError(input, errorElement, 'Name must be less than 100 characters.');
        return false;
    } else {
        hideFieldError(input, errorElement);
        return true;
    }
}

function validateEmail(input) {
    const value = input.value.trim();
    const errorElement = getOrCreateErrorElement(input);
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!value) {
        showFieldError(input, errorElement, 'Email is required.');
        return false;
    } else if (value.length > 100) {
        showFieldError(input, errorElement, 'Email must be less than 100 characters.');
        return false;
    } else if (!emailRegex.test(value)) {
        showFieldError(input, errorElement, 'Please enter a valid email address.');
        return false;
    } else {
        hideFieldError(input, errorElement);
        return true;
    }
}

function validateMessageLength(input) {
    const value = input.value;
    const errorElement = getOrCreateErrorElement(input);

    if (value.length > 1000) {
        showFieldError(input, errorElement, 'Message must be less than 1000 characters.');
        return false;
    } else {
        hideFieldError(input, errorElement);
        return true;
    }
}

function getOrCreateErrorElement(input) {
    let errorElement = input.parentNode.querySelector('.field-error');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        input.parentNode.appendChild(errorElement);
    }
    return errorElement;
}

function showFieldError(input, errorElement, message) {
    input.classList.add('error');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

function hideFieldError(input, errorElement) {
    input.classList.remove('error');
    errorElement.style.display = 'none';
}