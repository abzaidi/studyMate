// Form submission handling
document.getElementById('signup-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const email = e.target.querySelector('input[type="email"]').value;
    // Add your form submission logic here
    console.log('Form submitted with email:', email);
    alert('Thank you for signing up! We will be in touch soon.');
    e.target.reset();
});

// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.9)';
        navbar.style.boxShadow = 'none';
    }
});

// Smooth scroll for navigation links
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



const navContainer = document.getElementById('navContainer');
    const getStartedBtn = document.getElementById('getStartedBtn');
    const userBtn = document.getElementById('userBtn');
    const dropdownContent = document.getElementById('dropdownContent');

    // Function to simulate checking if user is logged in
    function isUserLoggedIn() {
        // Replace this with your actual authentication check
        return localStorage.getItem('isLoggedIn') === 'true';
    }

    // Function to update button visibility based on login state
    function updateNavigation() {
        if (isUserLoggedIn()) {
            getStartedBtn.style.display = 'none';
            userBtn.style.display = 'flex';
        } else {
            getStartedBtn.style.display = 'block';
            userBtn.style.display = 'none';
            dropdownContent.classList.remove('show');
        }
    }

    // Toggle dropdown when user button is clicked
    userBtn.addEventListener('click', function(event) {
        dropdownContent.classList.toggle('show');
        event.stopPropagation();
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        if (!navContainer.contains(event.target)) {
            dropdownContent.classList.remove('show');
        }
    });

    // Handle Get Started button click
    getStartedBtn.addEventListener('click', function() {
        // Replace with your sign up/login logic
        window.location.href = '/signup';
    });

    // Handle logout
    document.getElementById('logoutBtn').addEventListener('click', function(e) {
        e.preventDefault();
        // Replace with your logout logic
        localStorage.setItem('isLoggedIn', 'false');
        updateNavigation();
    });

    // For demo purposes - toggle login state
    // Remove this in production and replace with your actual auth logic
    function toggleLoginState() {
        localStorage.setItem('isLoggedIn', (!isUserLoggedIn()).toString());
        updateNavigation();
    }

    // Initialize navigation state
    updateNavigation();