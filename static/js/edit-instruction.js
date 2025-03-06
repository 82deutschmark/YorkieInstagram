
// Function to load all instructions
function loadInstructions() {
    fetch('/manage/instructions')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const instructionsList = document.getElementById('instructionsList');
                instructionsList.innerHTML = '';
                
                data.instructions.forEach(instruction => {
                    const item = document.createElement('div');
                    item.className = 'list-group-item d-flex justify-content-between align-items-center';
                    
                    const nameSpan = document.createElement('span');
                    nameSpan.textContent = instruction.name;
                    if (instruction.is_default) {
                        nameSpan.innerHTML += ' <span class="badge bg-success">Default</span>';
                    }
                    
                    const buttonsDiv = document.createElement('div');
                    buttonsDiv.className = 'btn-group';
                    
                    const editBtn = document.createElement('button');
                    editBtn.className = 'btn btn-sm btn-outline-primary';
                    editBtn.innerHTML = '<i class="fas fa-edit"></i>';
                    editBtn.addEventListener('click', () => editInstruction(instruction));
                    
                    const deleteBtn = document.createElement('button');
                    deleteBtn.className = 'btn btn-sm btn-outline-danger';
                    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                    deleteBtn.disabled = instruction.is_default;
                    deleteBtn.addEventListener('click', () => {
                        if (confirm(`Are you sure you want to delete "${instruction.name}"?`)) {
                            deleteInstruction(instruction.id);
                        }
                    });
                    
                    buttonsDiv.appendChild(editBtn);
                    buttonsDiv.appendChild(deleteBtn);
                    
                    item.appendChild(nameSpan);
                    item.appendChild(buttonsDiv);
                    instructionsList.appendChild(item);
                });
            }
        })
        .catch(error => {
            console.error('Error loading instructions:', error);
            showToast('Error', 'Failed to load Analysis Styles');
        });
}

// Function to edit an instruction (load values into form)
function editInstruction(instruction) {
    const form = document.getElementById('instructionForm');
    form.querySelector('[name="name"]').value = instruction.name;
    form.querySelector('[name="system_prompt"]').value = instruction.system_prompt;
    form.querySelector('[name="user_prompt"]').value = instruction.user_prompt;
    form.querySelector('[name="is_default"]').checked = instruction.is_default;
    
    // Store the ID for updating
    form.dataset.instructionId = instruction.id;
    
    // Change button text to indicate edit mode
    document.getElementById('saveInstructionBtn').textContent = 'Update';
}

// Function to delete an instruction
function deleteInstruction(id) {
    fetch('/manage/instructions', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: id })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Success', data.message);
            loadInstructions();
            
            // Refresh the dropdown in the main form
            refreshInstructionDropdown();
        } else {
            showToast('Error', data.error);
        }
    })
    .catch(error => {
        console.error('Error deleting instruction:', error);
        showToast('Error', 'Failed to delete Analysis Style');
    });
}

// Function to save a new instruction or update an existing one
function saveInstruction() {
    const form = document.getElementById('instructionForm');
    const instructionId = form.dataset.instructionId;
    
    const formData = {
        name: form.querySelector('[name="name"]').value,
        system_prompt: form.querySelector('[name="system_prompt"]').value,
        user_prompt: form.querySelector('[name="user_prompt"]').value,
        is_default: form.querySelector('[name="is_default"]').checked
    };
    
    // Validate form data
    if (!formData.name || !formData.system_prompt || !formData.user_prompt) {
        showToast('Error', 'All fields are required');
        return;
    }
    
    fetch('/manage/instructions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Success', `Analysis Style ${instructionId ? 'updated' : 'created'} successfully`);
            
            // Clear the form
            form.reset();
            delete form.dataset.instructionId;
            
            // Reset button text
            document.getElementById('saveInstructionBtn').textContent = 'Save';
            
            // Reload instructions list
            loadInstructions();
            
            // Refresh the dropdown in the main form
            refreshInstructionDropdown();
        } else {
            showToast('Error', data.error);
        }
    })
    .catch(error => {
        console.error('Error saving instruction:', error);
        showToast('Error', 'Failed to save Analysis Style');
    });
}

// Function to refresh the instruction dropdown in the main form
function refreshInstructionDropdown() {
    fetch('/manage/instructions')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const dropdown = document.getElementById('instruction');
                const selectedValue = dropdown.value;
                
                dropdown.innerHTML = '';
                
                data.instructions.forEach(instruction => {
                    const option = document.createElement('option');
                    option.value = instruction.id;
                    option.textContent = instruction.name;
                    option.selected = instruction.id == selectedValue;
                    dropdown.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error refreshing dropdown:', error);
        });
}

// Function to show toast notification
function showToast(title, message) {
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    const toast = bootstrap.Toast.getOrCreateInstance(document.getElementById('notificationToast'));
    
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    toast.show();
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Load instructions when modal is opened
    document.getElementById('instructionModal').addEventListener('show.bs.modal', loadInstructions);
    
    // Save button click handler
    document.getElementById('saveInstructionBtn').addEventListener('click', saveInstruction);
    
    // Reset form when modal is closed
    document.getElementById('instructionModal').addEventListener('hidden.bs.modal', function() {
        document.getElementById('instructionForm').reset();
        delete document.getElementById('instructionForm').dataset.instructionId;
        document.getElementById('saveInstructionBtn').textContent = 'Save';
    });
});
