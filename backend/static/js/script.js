
document.addEventListener('DOMContentLoaded', function() {
    // File Upload Handlers
    const uploadAreas = document.querySelectorAll('.upload-area');
    
    uploadAreas.forEach(area => {
        const fileInput = area.querySelector('.file-input');
        const fileType = area.dataset.type;
        const previewArea = area.querySelector('.file-preview');
        const fileInfo = document.getElementById(`${fileType}-info`);
        
        // Handle file selection
        fileInput.addEventListener('change', function() {
            handleFileSelection(this, fileType, previewArea, fileInfo);
        });
        
        // Drag and drop functionality
        area.addEventListener('dragover', function(e) {
            e.preventDefault();
            area.classList.add('drag-over');
        });
        
        area.addEventListener('dragleave', function() {
            area.classList.remove('drag-over');
        });
        
        area.addEventListener('drop', function(e) {
            e.preventDefault();
            area.classList.remove('drag-over');
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleFileSelection(fileInput, fileType, previewArea, fileInfo);
            }
        });
    });
    
    // Toggle between text upload and text entry
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const target = this.dataset.target;
            
            // Update active button state
            toggleBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Show the selected option
            document.querySelectorAll('.text-option').forEach(option => {
                option.classList.remove('active');
            });
            document.getElementById(target).classList.add('active');
        });
    });
    
    // Character counter for text entry
    const textArea = document.getElementById('user-text');
    const charCount = document.querySelector('.text-count');
    
    if (textArea && charCount) {
        textArea.addEventListener('input', function() {
            const count = this.value.length;
            charCount.textContent = `${count} character${count !== 1 ? 's' : ''}`;
        });
    }
});

// Handle file selection and preview
function handleFileSelection(input, fileType, previewArea, infoElement) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        const reader = new FileReader();
        
        // Update file info
        infoElement.innerHTML = `
            <i class="fa-solid fa-check-circle"></i>
            ${file.name} (${formatFileSize(file.size)})
        `;
        infoElement.classList.add('has-file');
        
        // Create preview based on file type
        reader.onload = function(e) {
            previewArea.innerHTML = '';
            previewArea.style.display = 'flex';
            
            if (fileType === 'image') {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'preview-content';
                previewArea.appendChild(img);
            } 
            else if (fileType === 'video') {
                const video = document.createElement('video');
                video.src = e.target.result;
                video.className = 'preview-content';
                video.controls = true;
                previewArea.appendChild(video);
            }
            else if (fileType === 'audio') {
                const audio = document.createElement('audio');
                audio.src = e.target.result;
                audio.className = 'preview-content';
                audio.controls = true;
                previewArea.appendChild(audio);
            }
            else if (fileType === 'text') {
                const div = document.createElement('div');
                div.className = 'text-preview-content';
                div.textContent = e.target.result.substring(0, 100) + (e.target.result.length > 100 ? '...' : '');
                previewArea.appendChild(div);
            }
            
            // Add remove button to preview
            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-file-btn';
            removeBtn.innerHTML = '<i class="fa-solid fa-times"></i>';
            removeBtn.onclick = function(event) {
                event.stopPropagation();
                clearFileInput(input);
                previewArea.style.display = 'none';
                infoElement.innerHTML = 'No file selected';
                infoElement.classList.remove('has-file');
                previewArea.innerHTML = '';
            };
            previewArea.appendChild(removeBtn);
        };
        
        if (fileType === 'text') {
            reader.readAsText(file);
        } else {
            reader.readAsDataURL(file);
        }
    }
}

// Format file size to readable format
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    
    return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + ' ' + sizes[i];
}

// Clear file input
function clearFileInput(input) {
    input.value = '';
}
