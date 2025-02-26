document.addEventListener('DOMContentLoaded', function () {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    const uploadBtn = document.getElementById('uploadBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const extractedText = document.getElementById('extractedText');
    const generateQuizBtn = document.getElementById('generateQuizBtn');
    const generateQABtn = document.getElementById('generateQABtn');

    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('drag-over');
    }

    function unhighlight() {
        dropZone.classList.remove('drag-over');
    }

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Handle file selection
    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            fileName.textContent = files[0].name;
            // Simulate file reading
            setTimeout(() => {
                extractedText.value = `Sample extracted text from ${files[0].name}.\n\nThis is where the content of your document would appear after processing.`;
            }, 1000);
        }
    }

    // Button handlers
    uploadBtn.addEventListener('click', function () {
        if (fileName.textContent) {
            alert('File uploaded successfully!');
        } else {
            alert('Please select a file first.');
        }
    });

    cancelBtn.addEventListener('click', function () {
        fileName.textContent = '';
        fileInput.value = '';
        extractedText.value = '';
    });

    generateQuizBtn.addEventListener('click', function () {
        if (extractedText.value) {
            alert('Generating quiz from the extracted text...');
        } else {
            alert('Please upload and process a file first.');
        }
    });

    generateQABtn.addEventListener('click', function () {
        if (extractedText.value) {
            alert('Generating Q&A pairs from the extracted text...');
        } else {
            alert('Please upload and process a file first.');
        }
    });
});

fetch('footer.html')
  .then(response => response.text())
  .then(html => {
    document.getElementById('footer-container').innerHTML = html;
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