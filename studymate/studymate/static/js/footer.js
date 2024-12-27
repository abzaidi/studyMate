 // Add smooth scrolling to all links
 document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Track link clicks for analytics
document.querySelectorAll('.footer-nav a, .social-links a').forEach(link => {
    link.addEventListener('click', function(e) {
        const linkText = this.textContent || this.getAttribute('aria-label');
        console.log(`Clicked: ${linkText}`);
        // Here you would typically send this data to your analytics service
    });
});