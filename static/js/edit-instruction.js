
/**
 * JavaScript for editing Analysis Styles in YorkieIG App
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to edit buttons after they're loaded
    fetchAndDisplayInstructions();
    
    // Handler for the instruction form submission
    document.getElementById('instructionForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const instructionId = document.getElementById('instructionId').value;
        
        // Prepare data object
        const data = {
            name: formData.get('name'),
            system_prompt: formData.get('system_prompt'),
            user_prompt: formData.get('user_prompt'),
            is_default: formData.get('is_default') === 'on'
        };
        
        // Determine if this is an edit or new instruction
        const method = instructionId ? 'PUT' : 'POST';
        if (instructionId) {
            data.id = instructionId;
        }
        
        // Send to the server
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
                // Hide modal and refresh instructions
                bootstrap.Modal.getInstance(document.getElementById('instructionModal')).hide();
                fetchAndDisplayInstructions();
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
function editInstruction(id) {
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

/**
 * Reset the instruction form
 */
function resetInstructionForm() {
    document.getElementById('instructionId').value = '';
    document.getElementById('instructionForm').reset();
}

/**
 * Show a toast notification
 * @param {string} title - The toast title
 * @param {string} message - The toast message
 */
function showToast(title, message) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        // Create toast container if it doesn't exist
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.id = 'toastContainer';
        document.body.appendChild(container);
    }
    
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" id="${toastId}">
            <div class="toast-header">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">${message}</div>
        </div>
    `;
    
    document.getElementById('toastContainer').insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Auto-remove after shown
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}
