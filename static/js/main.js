document.addEventListener('DOMContentLoaded', function() {
    const imageForm = document.getElementById('imageForm');
    const storyForm = document.getElementById('storyForm');
    const generateBtn = document.getElementById('generateBtn');
    const generateStoryBtn = document.getElementById('generateStoryBtn');
    const resultDiv = document.getElementById('result');
    const storyResultDiv = document.getElementById('storyResult');
    const generatedContent = document.getElementById('generatedContent');
    const generatedStory = document.getElementById('generatedStory');
    const copyBtn = document.getElementById('copyBtn');
    const copyStoryBtn = document.getElementById('copyStoryBtn');
    const toast = new bootstrap.Toast(document.getElementById('notificationToast'));
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    

    function showNotification(title, message, success = true) {
        toastTitle.textContent = title;
        toastMessage.textContent = message;
        document.getElementById('notificationToast').classList.toggle('bg-success', success);
        document.getElementById('notificationToast').classList.toggle('bg-danger', !success);
        toast.show();
    }
    

    if (imageForm) {
        imageForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
    

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    body: new FormData(imageForm)
                });
    

                const data = await response.json();
    

                if (response.ok) {
                    generatedContent.textContent = data.caption;
                    resultDiv.style.display = 'block';
                    showNotification('Success', 'Instagram post generated successfully!', true);
                } else {
                    showNotification('Error', data.error || 'Failed to generate post', false);
                }
            } catch (error) {
                showNotification('Error', 'An error occurred while generating the post', false);
            } finally {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Generate Post';
            }
        });
    }
    

    if (storyForm) {
        storyForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            generateStoryBtn.disabled = true;
            generateStoryBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
    

            try {
                const formData = new FormData(storyForm);
                const response = await fetch('/generate_story', {
                    method: 'POST',
                    body: formData
                });
    

                const data = await response.json();
    

                if (response.ok) {
                    generatedStory.textContent = data.story;
                    storyResultDiv.style.display = 'block';
                    showNotification('Success', 'Story generated successfully!', true);
                } else {
                    showNotification('Error', data.error || 'Failed to generate story', false);
                }
            } catch (error) {
                showNotification('Error', 'An error occurred while generating the story', false);
            } finally {
                generateStoryBtn.disabled = false;
                generateStoryBtn.innerHTML = '<i class="fas fa-book me-2"></i>Generate Story';
            }
        });
    }
    

    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(generatedContent.textContent)
                .then(() => showNotification('Success', 'Copied to clipboard!', true))
                .catch(() => showNotification('Error', 'Failed to copy text', false));
        });
    }
    

    if (copyStoryBtn) {
        copyStoryBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(generatedStory.textContent)
                .then(() => showNotification('Success', 'Story copied to clipboard!', true))
                .catch(() => showNotification('Error', 'Failed to copy story', false));
        });
    }
    

    function createCharacterCard(image, index) {
        return `
            <div class="character-gallery-col">
                <div class="card character-card">
                    <img src="${image.image_url}" class="card-img-top" alt="${image.name}">
                    <div class="card-body">
                        <h5 class="card-title">${image.name}</h5>
                        <p class="card-text small">${image.style}</p>
                        <p class="card-text">
                            <small class="text-muted">
                                Character Traits: ${image.character_traits.join(', ')}
                            </small>
                        </p>
                        <div class="btn-group d-flex justify-content-between mt-2">
                            <button class="btn btn-outline-primary btn-sm reroll-btn" data-index="${index}">
                                <i class="fas fa-dice"></i>
                            </button>
                            <button class="btn btn-outline-info btn-sm describe-btn" data-url="${image.image_url}">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-outline-success btn-sm select-btn" data-id="${image.id}">
                                <i class="fas fa-check"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    

    let currentImages = [];
    

    async function loadRandomCharacters() {
        try {
            const response = await fetch('/get_random_images');
            const data = await response.json();
    

            if (response.ok) {
                currentImages = data.images;
                const gallery = document.getElementById('characterGallery');
                gallery.innerHTML = currentImages.map((img, index) => createCharacterCard(img, index)).join('');
                attachEventListeners();
            } else {
                showNotification('Error', data.error || 'Failed to load characters', false);
            }
        } catch (error) {
            showNotification('Error', 'An error occurred while loading characters', false);
        }
    }
    

    async function handleReroll(event) {
        const button = event.currentTarget;
        const index = parseInt(button.dataset.index);
        const excludedIds = currentImages.map(img => img.id);
    

        try {
            const params = new URLSearchParams();
            excludedIds.forEach(id => params.append('excluded_ids[]', id));
    

            const response = await fetch(`/reroll_image/${index}?${params.toString()}`);
            const data = await response.json();
    

            if (response.ok) {
                currentImages[index] = data.image;
                const cardContainer = button.closest('.character-gallery-col');
                cardContainer.outerHTML = createCharacterCard(data.image, index);
                attachEventListeners();
            } else {
                showNotification('Error', data.error || 'Failed to reroll character', false);
            }
        } catch (error) {
            showNotification('Error', 'An error occurred while rerolling character', false);
        }
    }
    

    function handleSelect(event) {
        const button = event.currentTarget;
        const imageId = button.dataset.id;
    

        // Update hidden input
        document.getElementById('selectedImageId').value = imageId;
    

        // Update UI to show selection
        document.querySelectorAll('.select-btn').forEach(btn => {
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-success');
        });
        button.classList.remove('btn-outline-success');
        button.classList.add('btn-success');
    

        showNotification('Success', 'Character selected for the story!', true);
    }
    

    async function handleDescribe(event) {
        const button = event.currentTarget;
        const imageUrl = button.dataset.url;
    

        button.disabled = true;
        const originalHtml = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    

        try {
            const response = await fetch('/analyze_image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image_url: imageUrl })
            });
    

            const data = await response.json();
    

            if (response.ok) {
                // Find the card and update its content
                const card = button.closest('.character-card');
                card.querySelector('.card-title').textContent = data.analysis.name || 'Unnamed Character';
                card.querySelector('.card-text.small').textContent = data.analysis.style || 'Style not specified';
                card.querySelector('.text-muted').textContent = 
                    'Character Traits: ' + (data.analysis.character_traits || []).join(', ');
    

                showNotification('Success', 'Image analyzed successfully!', true);
            } else {
                showNotification('Error', data.error || 'Failed to analyze image', false);
            }
        } catch (error) {
            showNotification('Error', 'An error occurred while analyzing the image', false);
        } finally {
            button.disabled = false;
            button.innerHTML = originalHtml;
        }
    }
    

    // Add describe button event listeners
    function attachEventListeners() {
        document.querySelectorAll('.reroll-btn').forEach(btn => {
            btn.addEventListener('click', handleReroll);
        });
    

        document.querySelectorAll('.describe-btn').forEach(btn => {
            btn.addEventListener('click', handleDescribe);
        });
    

        document.querySelectorAll('.select-btn').forEach(btn => {
            btn.addEventListener('click', handleSelect);
        });
    }
    

    const loadCharactersBtn = document.getElementById('loadCharactersBtn');
    if (loadCharactersBtn) {
        loadCharactersBtn.addEventListener('click', loadRandomCharacters);
        loadRandomCharacters();
    }
});