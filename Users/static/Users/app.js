document.addEventListener('DOMContentLoaded', () => {
    // A single event listener on the main content area
    const mainContent = document.getElementById('main-content');
    
    if (mainContent) {
        mainContent.addEventListener('click', (event) => {
            const target = event.target;

            // --- Handle Favorite Button Clicks ---
            // .closest() finds the nearest parent with the specified class
            const favoriteButton = target.closest('.btn-favorite');
            if (favoriteButton) {
                const icon = favoriteButton.querySelector('.fa-heart');
                icon.classList.toggle('far'); // Empty heart
                icon.classList.toggle('fas'); // Solid heart
                
                const isFavorited = icon.classList.contains('fas');
                favoriteButton.setAttribute('aria-label', isFavorited ? 'Remove from favorites' : 'Add to favorites');
                
                // You would add an API call here to save the favorite status
                const turfId = favoriteButton.closest('.turf-card').dataset.turfId;
                console.log(`Toggled favorite for turf ID: ${turfId}`);
                return; // Stop further processing
            }

            // --- Handle Booking Card Clicks ---
            const bookingCard = target.closest('.booking-card');
            if (bookingCard) {
                // Prevent clicks on buttons inside the card from triggering this
                if (target.closest('a')) return; 

                const bookingId = bookingCard.dataset.bookingId;
                console.log(`Booking card clicked for booking ID: ${bookingId}. Opening details...`);
                // In a real app, you would redirect or open a modal:
                // window.location.href = `/bookings/${bookingId}/`;
                return;
            }
        });
    }

    // --- Notification Button Logic (kept separate as it's in the header) ---
    const notificationBtn = document.querySelector('.notification-btn');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', () => {
            console.log('Notifications would appear here.');
            // A more robust UI (like a dropdown) would be better than an alert
            const badge = notificationBtn.querySelector('.notification-badge');
            if (badge) {
                badge.style.display = 'none';
            }
        });
    }
});