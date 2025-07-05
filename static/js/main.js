/**
 * AIFLIX - Main JavaScript File
 * Contains common functionality used across the site
 */

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover'
        });
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            trigger: 'hover',
            html: true
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.matches('.dropdown-toggle')) {
            var dropdowns = document.getElementsByClassName('dropdown-menu');
            for (var i = 0; i < dropdowns.length; i++) {
                var openDropdown = dropdowns[i];
                if (openDropdown.classList.contains('show')) {
                    openDropdown.classList.remove('show');
                }
            }
        }
    });

    // Auto-hide navbar on scroll down, show on scroll up
    let lastScrollTop = 0;
    const navbar = document.querySelector('.navbar');
    
    if (navbar) {
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                // Scrolling down
                navbar.classList.add('navbar-hide');
            } else {
                // Scrolling up
                navbar.classList.remove('navbar-hide');
            }
            
            // Add/remove navbar background on scroll
            if (scrollTop > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
            
            lastScrollTop = scrollTop;
        });
    }
});

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, info, warning)
 * @param {number} delay - Time in milliseconds to show the toast (default: 3000)
 */
function showToast(message, type = 'info', delay = 3000) {
    const toastEl = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    
    if (!toastEl || !toastMessage) return;
    
    // Set message and styling based on type
    toastMessage.textContent = message;
    
    // Remove previous type classes
    const toastHeader = toastEl.querySelector('.toast-header');
    toastHeader.className = 'toast-header';
    
    // Set header class based on type
    switch(type) {
        case 'success':
            toastHeader.classList.add('bg-success', 'text-white');
            break;
        case 'error':
            toastHeader.classList.add('bg-danger', 'text-white');
            break;
        case 'warning':
            toastHeader.classList.add('bg-warning', 'text-dark');
            break;
        default: // info
            toastHeader.classList.add('bg-primary', 'text-white');
    }
    
    // Show the toast
    const toast = new bootstrap.Toast(toastEl, {
        animation: true,
        autohide: true,
        delay: delay
    });
    
    toast.show();
}

/**
 * Toggle password visibility
 * @param {HTMLElement} inputElement - The password input element
 * @param {HTMLElement} toggleElement - The toggle button element
 */
function togglePasswordVisibility(inputElement, toggleElement) {
    if (inputElement.type === 'password') {
        inputElement.type = 'text';
        toggleElement.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
        inputElement.type = 'password';
        toggleElement.innerHTML = '<i class="fas fa-eye"></i>';
    }
}

/**
 * Toggle "My List" status for a movie
 * @param {number} movieId - The ID of the movie
 * @param {HTMLElement} button - The button element that was clicked
 */
function toggleMyList(movieId, button) {
    const url = `/profiles/toggle-my-list/${movieId}/`;
    const isInList = button.dataset.inList === 'true';
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'removed') {
            button.innerHTML = '<i class="far fa-plus me-1"></i> Add to List';
            button.classList.remove('btn-outline-light');
            button.classList.add('btn-outline-secondary');
            button.dataset.inList = 'false';
            
            // If we're on the My List page, remove the item from the DOM
            if (window.location.pathname.includes('my-list')) {
                const movieCard = button.closest('.col');
                if (movieCard) {
                    movieCard.style.opacity = '0.5';
                    setTimeout(() => {
                        movieCard.remove();
                        
                        // Check if we should show the empty state
                        const remainingItems = document.querySelectorAll('.movie-card').length;
                        if (remainingItems === 0) {
                            window.location.reload();
                        }
                    }, 300);
                }
            }
            
            showToast('Removed from My List', 'success');
        } else if (data.status === 'added') {
            button.innerHTML = '<i class="fas fa-check me-1"></i> In My List';
            button.classList.remove('btn-outline-secondary');
            button.classList.add('btn-outline-light');
            button.dataset.inList = 'true';
            
            showToast('Added to My List', 'success');
        } else if (data.status === 'error') {
            showToast(data.message || 'An error occurred', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
    });
}

/**
 * Get cookie value by name
 * @param {string} name - The name of the cookie
 * @returns {string} The cookie value or an empty string if not found
 */
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
    return cookieValue || '';
}

// Make functions available globally
window.AIFLIX = {
    showToast,
    togglePasswordVisibility,
    toggleMyList
};
