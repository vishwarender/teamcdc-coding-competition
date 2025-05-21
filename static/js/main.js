// Shared JavaScript functionality for Bandaranayake College Coding Competition

// Show success alerts for 3 seconds and then fade out
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            setTimeout(function() {
                bsAlert.close();
            }, 5000);
        });
    }, 100);

    // Enable all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Prevent form resubmission on refresh
    if (window.history.replaceState) {
        window.history.replaceState(null, null, window.location.href);
    }
});

// Function to validate file size before upload
function validateFileSize(input, maxSizeMB) {
    const maxSize = maxSizeMB * 1024 * 1024; // MB to bytes
    if (input.files[0] && input.files[0].size > maxSize) {
        alert(`File is too large. Maximum size is ${maxSizeMB}MB.`);
        input.value = ''; // Clear the input
        return false;
    }
    return true;
}

// Create progress bar
function createProgressBar(fileInput) {
    const container = fileInput.parentElement;
    let progressDiv = container.querySelector('.upload-progress');
    if (!progressDiv) {
        progressDiv = document.createElement('div');
        progressDiv.className = 'upload-progress progress mt-2 d-none';
        progressDiv.innerHTML = `
            <div class="progress-bar" role="progressbar" style="width: 0%" 
                 aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>`;
        container.appendChild(progressDiv);
    }
    return progressDiv;
}

// Update progress bar
function updateProgress(progressDiv, percent) {
    const progressBar = progressDiv.querySelector('.progress-bar');
    progressBar.style.width = `${percent}%`;
    progressBar.setAttribute('aria-valuenow', percent);
}

// Handle form submission with progress
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            
            // Show progress bars
            const fileInputs = form.querySelectorAll('input[type="file"]');
            fileInputs.forEach(input => {
                if (input.files.length > 0) {
                    const progressDiv = createProgressBar(input);
                    progressDiv.classList.remove('d-none');
                }
            });

            // Submit form with progress
            fetch(form.action, {
                method: 'POST',
                body: formData
            }).then(response => {
                if (response.ok) {
                    window.location.reload();
                }
            }).catch(error => {
                console.error('Error:', error);
                alert('Upload failed. Please try again.');
            });
        });
    }
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            validateFileSize(this, 100); // 100MB max
        });
    });
});
