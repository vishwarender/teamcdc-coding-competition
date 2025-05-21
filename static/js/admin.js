// JavaScript for Admin Dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Handle participant detail modal
    const viewButtons = document.querySelectorAll('.view-details');
    const participantModal = document.getElementById('participantModal');
    const participantDetails = document.getElementById('participantDetails');
    
    if (viewButtons.length > 0 && participantModal && participantDetails) {
        viewButtons.forEach(button => {
            button.addEventListener('click', function() {
                const participantId = this.getAttribute('data-id');
                
                // Show loading spinner
                participantDetails.innerHTML = `
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>
                `;
                
                // Open modal
                const modal = new bootstrap.Modal(participantModal);
                modal.show();
                
                // Fetch participant details
                fetch(`/admin/participant/${participantId}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        // Populate modal with participant details
                        let teamMembersHtml = '';
                        if (data.team_members && data.team_members.length > 0) {
                            teamMembersHtml = `
                                <h5 class="mt-4">Team Members</h5>
                                <table class="table table-bordered table-sm">
                                    <thead class="table-light">
                                        <tr>
                                            <th>Name</th>
                                            <th>WhatsApp Number</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${data.team_members.map(member => `
                                            <tr>
                                                <td>${member.name}</td>
                                                <td>${member.whatsapp_number}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            `;
                        }
                        
                        participantDetails.innerHTML = `
                            <div class="row">
                                <div class="col-md-6">
                                    <h5>Participant Information</h5>
                                    <table class="table table-bordered">
                                        <tr>
                                            <th>Full Name</th>
                                            <td>${data.full_name}</td>
                                        </tr>
                                        <tr>
                                            <th>Grade</th>
                                            <td>Grade ${data.grade}</td>
                                        </tr>
                                        <tr>
                                            <th>WhatsApp Number</th>
                                            <td>${data.whatsapp_number}</td>
                                        </tr>
                                        <tr>
                                            <th>School</th>
                                            <td>${data.school}</td>
                                        </tr>
                                        <tr>
                                            <th>Team Size</th>
                                            <td>${data.team_members_count}</td>
                                        </tr>
                                        <tr>
                                            <th>Registration Date</th>
                                            <td>${data.registration_date}</td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h5>Additional Information</h5>
                                    <table class="table table-bordered">
                                        <tr>
                                            <th>Society Name</th>
                                            <td>${data.society_name || '-'}</td>
                                        </tr>
                                        <tr>
                                            <th>President Name</th>
                                            <td>${data.president_name || '-'}</td>
                                        </tr>
                                        <tr>
                                            <th>President Number</th>
                                            <td>${data.president_number || '-'}</td>
                                        </tr>
                                        <tr>
                                            <th>Teacher Name</th>
                                            <td>${data.teacher_name || '-'}</td>
                                        </tr>
                                        <tr>
                                            <th>Teacher Number</th>
                                            <td>${data.teacher_number || '-'}</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                            ${teamMembersHtml}
                        `;
                    })
                    .catch(error => {
                        participantDetails.innerHTML = `
                            <div class="alert alert-danger" role="alert">
                                Error loading participant details: ${error.message}
                            </div>
                        `;
                    });
            });
        });
    }
    
    // Filter form automatic submission
    const filterForms = document.querySelectorAll('#filterForm');
    filterForms.forEach(form => {
        const inputs = form.querySelectorAll('select, input');
        inputs.forEach(input => {
            if (input.tagName.toLowerCase() === 'select') {
                input.addEventListener('change', function() {
                    form.submit();
                });
            }
        });
    });
});
