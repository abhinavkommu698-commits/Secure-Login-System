// Main JavaScript for Secure Login System

// Auto-dismiss flash messages after 5 seconds
function initFlashMessages() {
  setTimeout(function() {
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
      const bsAlert = new bootstrap.Alert(message);
      bsAlert.close();
    });
  }, 5000);
}

// Toggle password visibility
function togglePassword(inputId, button) {
  const input = document.getElementById(inputId);
  const icon = button.querySelector('i');
  
  if (input.type === 'password') {
    input.type = 'text';
    icon.classList.remove('bi-eye-slash');
    icon.classList.add('bi-eye');
  } else {
    input.type = 'password';
    icon.classList.remove('bi-eye');
    icon.classList.add('bi-eye-slash');
  }
}

// Password strength checker
function checkPasswordStrength(password) {
  const strengthFill = document.getElementById('strengthFill');
  if (!strengthFill) return;
  
  let strength = 0;
  
  if (password.length >= 8) strength++;
  if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
  if (password.match(/\d/)) strength++;
  if (password.match(/[^a-zA-Z\d]/)) strength++;
  
  const strengthClasses = ['', 'strength-weak', 'strength-fair', 'strength-good', 'strength-strong'];
  strengthFill.className = 'password-strength-fill ' + strengthClasses[strength];
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  initFlashMessages();
  
  // Add password strength listeners
  const passwordInput = document.getElementById('passwordInput');
  if (passwordInput) {
    passwordInput.addEventListener('input', function() {
      checkPasswordStrength(this.value);
    });
  }
});
