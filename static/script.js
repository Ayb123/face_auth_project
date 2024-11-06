document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const flashMessages = document.getElementById('flash-messages');
        if (flashMessages) {
            flashMessages.style.display = 'none';
        }
    }, 4000);  // 4 seconds
});
