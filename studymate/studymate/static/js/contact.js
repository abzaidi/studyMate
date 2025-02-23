//  // Navbar scroll effect
//  window.addEventListener('scroll', function() {
//     const navbar = document.querySelector('.navbar');
//     if (window.scrollY > 50) {
//         navbar.style.background = 'rgba(255, 255, 255, 0.95)';
//         navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
//     } else {
//         navbar.style.background = 'rgba(255, 255, 255, 0.9)';
//         navbar.style.boxShadow = 'none';
//     }
// });

// // Form validation and submission
// const form = document.getElementById('contactForm');
// const submitBtn = document.getElementById('submitBtn');
// const nameError = document.getElementById('nameError');
// const emailError = document.getElementById('emailError');
// const messageError = document.getElementById('messageError');

// function validateEmail(email) {
//     const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
//     return re.test(email);
// }

// function validateForm() {
//     let isValid = true;
//     const name = document.getElementById('name').value;
//     const email = document.getElementById('email').value;
//     const message = document.getElementById('message').value;

//     // Reset error messages
//     nameError.textContent = '';
//     emailError.textContent = '';
//     messageError.textContent = '';

//     if (name.length < 2) {
//         nameError.textContent = 'Name must be at least 2 characters long';
//         isValid = false;
//     }

//     if (!validateEmail(email)) {
//         emailError.textContent = 'Please enter a valid email address';
//         isValid = false;
//     }

//     if (message.length < 10) {
//         messageError.textContent = 'Message must be at least 10 characters long';
//         isValid = false;
//     }

//     return isValid;
// }

// form.addEventListener('submit', function(e) {
//     e.preventDefault();

//     if (validateForm()) {
//         submitBtn.disabled = true;
//         submitBtn.textContent = 'Sending...';

//         // Simulate form submission
//         setTimeout(() => {
//             alert('Thank you for your message! We will get back to you soon.');
//             form.reset();
//             submitBtn.disabled = false;
//             submitBtn.textContent = 'Submit';
//         }, 1500);
//     }
// });

// fetch('footer.html')
//   .then(response => response.text())
//   .then(html => {
//     document.getElementById('footer-container').innerHTML = html;
//   });

// // Real-time validation
// const inputs = form.querySelectorAll('input, textarea');
// inputs.forEach(input => {
//     input.addEventListener('input', () => {
//         validateForm();
//     });
// });


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