// Main JavaScript file for the e-commerce platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Handle product card hover effects
    const productCards = document.querySelectorAll('.card');
    if (productCards) {
        productCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.classList.add('shadow');
            });
            
            card.addEventListener('mouseleave', function() {
                this.classList.remove('shadow');
            });
        });
    }
});
