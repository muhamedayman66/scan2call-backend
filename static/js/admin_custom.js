// Custom admin JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('scan2call Admin loaded');
    
    // Add custom functionality here
    const headers = document.querySelectorAll('.admin-header');
    headers.forEach(header => {
        header.style.animation = 'fadeIn 0.5s ease-in';
    });
});