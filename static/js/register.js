// JavaScript for the Registration Form

document.addEventListener('DOMContentLoaded', function() {
    const teamMembersCount = document.getElementById('teamMembersCount');
    const teamMembersContainer = document.getElementById('teamMembersContainer');
    
    // Generate team member fields based on selected count
    function generateTeamMemberFields() {
        // Clear previous fields
        teamMembersContainer.innerHTML = '';
        
        // Get selected count (subtract 1, since the main participant is already included)
        const count = parseInt(teamMembersCount.value) - 1;
        
        // If solo (count = 0), don't generate any fields
        if (count <= 0) {
            return;
        }
        
        // Add team member fields
        for (let i = 1; i <= count; i++) {
            const memberFields = document.createElement('div');
            memberFields.className = 'card mb-3';
            memberFields.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">Team Member ${i}</h5>
                    <div class="mb-3">
                        <label for="member_name_${i}" class="form-label">Full Name *</label>
                        <input type="text" class="form-control" id="member_name_${i}" name="member_name_${i}" required>
                    </div>
                    <div class="mb-3">
                        <label for="member_whatsapp_${i}" class="form-label">WhatsApp Number *</label>
                        <input type="text" class="form-control" id="member_whatsapp_${i}" name="member_whatsapp_${i}" required>
                        <div class="form-text">Please include country code (e.g., +94)</div>
                    </div>
                </div>
            `;
            teamMembersContainer.appendChild(memberFields);
        }
    }
    
    // Initial generation
    if (teamMembersCount) {
        generateTeamMemberFields();
        
        // Update when count changes
        teamMembersCount.addEventListener('change', generateTeamMemberFields);
    }
    
    // Form validation
    const registrationForm = document.getElementById('registrationForm');
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(event) {
            const termsCheck = document.getElementById('termsCheck');
            
            // Validate terms checkbox
            if (!termsCheck.checked) {
                event.preventDefault();
                alert('Please agree to the rules and guidelines before registering.');
                return false;
            }
            
            // Validate WhatsApp number format
            const whatsappNumber = document.getElementById('whatsapp_number');
            if (whatsappNumber && !/^\+?\d{10,15}$/.test(whatsappNumber.value)) {
                event.preventDefault();
                alert('Please enter a valid WhatsApp number.');
                whatsappNumber.focus();
                return false;
            }
            
            // Validate team member WhatsApp numbers if applicable
            const count = parseInt(teamMembersCount.value) - 1;
            for (let i = 1; i <= count; i++) {
                const memberWhatsapp = document.getElementById(`member_whatsapp_${i}`);
                if (memberWhatsapp && !/^\+?\d{10,15}$/.test(memberWhatsapp.value)) {
                    event.preventDefault();
                    alert(`Please enter a valid WhatsApp number for Team Member ${i}.`);
                    memberWhatsapp.focus();
                    return false;
                }
            }
            
            return true;
        });
    }
});
