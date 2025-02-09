//  // Form elements
//  const authForm = document.getElementById('authForm');
//  const formTitle = document.getElementById('formTitle');
//  const formDescription = document.getElementById('formDescription');
//  const nameGroup = document.getElementById('nameGroup');
//  const toggleBtn = document.getElementById('toggleBtn');
//  const toggleText = document.getElementById('toggleText');
//  const submitBtn = document.getElementById('submitBtn');

//  // Form state
//  let isLogin = true;

//  // Toggle between login and signup
//  toggleBtn.addEventListener('click', (e) => {
//      e.preventDefault();
//      isLogin = !isLogin;
     
//      // Update UI
//      formTitle.textContent = isLogin ? 'Login' : 'Sign Up';
//      formDescription.textContent = isLogin 
//          ? 'Welcome back! Please enter your details.'
//          : 'Create an account to get started.';
//      nameGroup.style.display = isLogin ? 'none' : 'block';
//      submitBtn.textContent = isLogin ? 'Login' : 'Sign Up';
//      toggleText.innerHTML = isLogin 
//          ? 'Don\'t have an account? <a href="#" id="toggleBtn">Sign up</a>'
//          : 'Already have an account? <a href="#" id="toggleBtn">Login</a>';
     
//      // Reset form
//      authForm.reset();
//      clearErrors();
//  });

//  // Form validation
//  function validateForm() {
//      let isValid = true;
//      clearErrors();

//      // Name validation (for signup)
//      if (!isLogin) {
//          const name = document.getElementById('name').value;
//          if (name.length < 2) {
//              showError('name', 'Name must be at least 2 characters long');
//              isValid = false;
//          }
//      }

//      // Email validation
//      const email = document.getElementById('email').value;
//      if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
//          showError('email', 'Please enter a valid email address');
//          isValid = false;
//      }

//      // Password validation
//      const password = document.getElementById('password').value;
//      if (password.length < 6) {
//          showError('password', 'Password must be at least 6 characters long');
//          isValid = false;
//      }

//      return isValid;
//  }

//  function showError(field, message) {
//      const errorElement = document.getElementById(`${field}Error`);
//      errorElement.textContent = message;
//      errorElement.style.display = 'block';
//  }

//  function clearErrors() {
//      const errors = document.getElementsByClassName('error-message');
//      Array.from(errors).forEach(error => error.style.display = 'none');
//  }

//  // Form submission
//  authForm.addEventListener('submit', (e) => {
//      e.preventDefault();

//      if (validateForm()) {
//          // Simulate form submission
//          submitBtn.disabled = true;
//          submitBtn.textContent = isLogin ? 'Logging in...' : 'Signing up...';

//          setTimeout(() => {
//              // Here you would typically make an API call
//              alert(isLogin ? 'Login successful!' : 'Account created successfully!');
//              submitBtn.disabled = false;
//              submitBtn.textContent = isLogin ? 'Login' : 'Sign Up';
//              if (!isLogin) {
//                  // Switch to login after successful signup
//                  toggleBtn.click();
//              }
//          }, 1500);
//      }
//  });

// //  fetch('footer.html')
// //   .then(response => response.text())
// //   .then(html => {
// //     document.getElementById('footer-container').innerHTML = html;
// //   });