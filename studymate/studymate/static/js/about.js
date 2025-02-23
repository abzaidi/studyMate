document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.querySelector('.nav-links');

    // Toggle mobile menu
    mobileMenuBtn.addEventListener('click', function () {
        navLinks.classList.toggle('active');

        // Animate hamburger to X
        this.classList.toggle('active');

        if (this.classList.contains('active')) {
            this.children[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            this.children[1].style.opacity = '0';
            this.children[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
        } else {
            this.children[0].style.transform = 'none';
            this.children[1].style.opacity = '1';
            this.children[2].style.transform = 'none';
        }
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function (event) {
        if (!event.target.closest('.navbar')) {
            navLinks.classList.remove('active');
            mobileMenuBtn.classList.remove('active');

            Array.from(mobileMenuBtn.children).forEach(span => {
                span.style.transform = 'none';
                span.style.opacity = '1';
            });
        }
    });

    // Handle window resize
    window.addEventListener('resize', function () {
        if (window.innerWidth > 768) {
            navLinks.classList.remove('active');
            mobileMenuBtn.classList.remove('active');

            Array.from(mobileMenuBtn.children).forEach(span => {
                span.style.transform = 'none';
                span.style.opacity = '1';
            });
        }
    });


    // Add smooth scroll for team member cards
    const teamMembers = document.querySelectorAll('.team-member');
    teamMembers.forEach(member => {
        member.addEventListener('mouseenter', () => {
            member.style.transform = 'translateY(-5px)';
        });

        member.addEventListener('mouseleave', () => {
            member.style.transform = 'translateY(0)';
        });
    });

    fetch('footer.html')
  .then(response => response.text())
  .then(html => {
    document.getElementById('footer-container').innerHTML = html;
  });
});



const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

hamburger.addEventListener('click', () => {
    // Toggle active class for hamburger animation
    hamburger.classList.toggle('active');
    // Toggle nav links visibility
    navLinks.classList.toggle('active');
});

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
        hamburger.classList.remove('active');
        navLinks.classList.remove('active');
    }
});

// Close mobile menu when clicking a link
navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navLinks.classList.remove('active');
    });
});