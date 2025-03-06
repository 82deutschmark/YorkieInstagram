/**
 * JavaScript for editing Analysis Styles in YorkieIG App
 */

document.addEventListener('DOMContentLoaded', function() {
    // Function to reset the instruction form
    function resetInstructionForm() {
        const form = document.getElementById('instructionForm');
        form.reset();
        document.getElementById('instructionId').value = '';
    }

    // Function to show toast notifications
    function showToast(title, message) {
        const toastEl = document.getElementById('toast');
        const toastTitle = document.querySelector('#toast .toast-header strong');
        const toastBody = document.querySelector('#toast .toast-body');

        toastTitle.textContent = title;
        toastBody.textContent = message;

        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    }

    // Function to edit an instruction
    window.editInstruction = function(id) {
        fetch(`/get_instruction/${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const instruction = data.instruction;

                    // Reset form
                    resetInstructionForm();

                    // Set modal title
                    document.getElementById('instructionModalTitle').textContent = 'Edit Analysis Style';

                    // Fill form with instruction data
                    document.getElementById('instructionId').value = instruction.id;
                    document.querySelector('#instructionForm input[name="name"]').value = instruction.name;
                    document.querySelector('#instructionForm textarea[name="system_prompt"]').value = instruction.system_prompt;
                    document.querySelector('#instructionForm textarea[name="user_prompt"]').value = instruction.user_prompt;
                    document.querySelector('#instructionForm input[name="is_default"]').checked = instruction.is_default;

                    // Show modal
                    const modal = new bootstrap.Modal(document.getElementById('instructionModal'));
                    modal.show();
                } else {
                    showToast('Error', data.error || 'Failed to load Analysis Style');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error', 'Failed to load Analysis Style');
            });
    }

    // Add event listeners to edit buttons after they're loaded
    fetchAndDisplayInstructions();
    
    // Form submission handler
    document.getElementById('instructionForm').addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const instructionId = document.getElementById('instructionId').value;

        // Prepare data for API call
        const data = {
            name: formData.get('name'),
            system_prompt: formData.get('system_prompt'),
            user_prompt: formData.get('user_prompt'),
            is_default: formData.get('is_default') === 'on'
        };

        // If instructionId exists, add it to the data for update
        if (instructionId) {
            data.id = instructionId;
        }

        // Determine if this is a create or update operation
        const method = instructionId ? 'PUT' : 'POST';

        // Send to server
        fetch('/manage/instructions', {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('instructionModal'));
                modal.hide();

                // Reload page to show changes
                window.location.reload();

                showToast('Success', 'Analysis Style saved successfully');
            } else {
                showToast('Error', data.error || 'Failed to save Analysis Style');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error', 'Failed to save Analysis Style');
        });
    });

    // Handler for "Add New" button
    document.querySelector('[data-bs-target="#instructionModal"]').addEventListener('click', function() {
        resetInstructionForm();
        document.getElementById('instructionModalTitle').textContent = 'Create New Analysis Style';
    });
});

/**
 * Fetch and display all instructions
 */
function fetchAndDisplayInstructions() {
    fetch('/manage/instructions')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Get the instruction dropdown
                const instructionSelect = document.getElementById('instruction');
                const currentValue = instructionSelect.value;
                
                // Clear existing options
                instructionSelect.innerHTML = '';
                
                // Add instructions to dropdown
                data.instructions.forEach(instruction => {
                    const option = document.createElement('option');
                    option.value = instruction.id;
                    option.textContent = instruction.name + (instruction.is_default ? ' (Default)' : '');
                    option.dataset.isDefault = instruction.is_default;
                    instructionSelect.appendChild(option);
                });
                
                // Restore selected value if possible
                if (currentValue) {
                    instructionSelect.value = currentValue;
                }
                
                // Create a list of instructions with edit buttons
                const instructionsList = document.getElementById('instructionsList');
                if (instructionsList) {
                    instructionsList.innerHTML = '';
                    
                    data.instructions.forEach(instruction => {
                        const item = document.createElement('div');
                        item.className = 'list-group-item d-flex justify-content-between align-items-center';
                        
                        const name = document.createElement('span');
                        name.textContent = instruction.name + (instruction.is_default ? ' (Default)' : '');
                        
                        const editBtn = document.createElement('button');
                        editBtn.className = 'btn btn-sm btn-outline-primary';
                        editBtn.textContent = 'Edit';
                        editBtn.addEventListener('click', () => editInstruction(instruction.id));
                        
                        item.appendChild(name);
                        item.appendChild(editBtn);
                        instructionsList.appendChild(item);
                    });
                } else {
                    // Create the list-group if it doesn't exist
                    const modal = document.getElementById('instructionModal');
                    const modalBody = modal.querySelector('.modal-body');
                    
                    const listHeading = document.createElement('h6');
                    listHeading.className = 'mt-4 mb-2';
                    listHeading.textContent = 'Edit Existing Styles';
                    
                    const listGroup = document.createElement('div');
                    listGroup.className = 'list-group mb-3';
                    listGroup.id = 'instructionsList';
                    
                    // Add to modal
                    modalBody.appendChild(listHeading);
                    modalBody.appendChild(listGroup);
                    
                    // Refresh to populate the list
                    fetchAndDisplayInstructions();
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

/**
 * Edit an existing instruction
 * @param {number} id - The instruction ID to edit
 */

/**
 * Reset the instruction form
 */


/**
 * Show a toast notification
 * @param {string} title - The toast title
 * @param {string} message - The toast message
 */