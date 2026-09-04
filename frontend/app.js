const scaleInput = document.getElementById('scale');
const scaleVal = document.getElementById('scaleVal');
const form = document.getElementById('screenForm');
const fileInput = document.getElementById('resumes');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const candidatesList = document.getElementById('candidatesList');

// Global lookup array to keep local File object mappings persistent during runtime view requests
let uploadedFilesCache = [];

// Dynamic slider text updating
scaleInput.addEventListener('input', (e) => {
    scaleVal.textContent = e.target.value;
});

// Update standard file field styling text hint when selecting assets
fileInput.addEventListener('change', (e) => {
    const hint = document.querySelector('.file-hint');
    if(e.target.files.length > 0) {
        hint.innerHTML = `<strong>${e.target.files.length}</strong> file(s) staging selected`;
        // Cache files internally mapped out by unique target criteria names
        uploadedFilesCache = Array.from(e.target.files);
    } else {
        hint.textContent = "Click to select or drag files here";
        uploadedFilesCache = [];
    }
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    candidatesList.innerHTML = '';

    const formData = new FormData();
    
    if (uploadedFilesCache.length === 0) {
        alert("Please select files before running evaluation.");
        loading.classList.add('hidden');
        return;
    }

    uploadedFilesCache.forEach(file => {
        formData.append('resumes', file);
    });
    
    formData.append('job_description', document.getElementById('job_description').value);
    formData.append('scale', scaleInput.value);
    formData.append('filter_education', document.getElementById('filter_education').value);
    formData.append('filter_min_exp', document.getElementById('filter_min_exp').value);
    formData.append('filter_max_exp', document.getElementById('filter_max_exp').value);
    formData.append('filter_universities', document.getElementById('filter_universities').value);

    try {
        const response = await fetch('http://127.0.0.1:5000/screen', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.shortlisted) {
            if (data.shortlisted.length === 0) {
                candidatesList.innerHTML = '<div style="text-align:center; padding:20px; color:#64748b;">No matching candidates found after evaluating scaling constraints and input filters.</div>';
            } else {
                data.shortlisted.forEach(cand => {
                    // Try to map structure matching file inside user local browser storage frame
                    const matchingRawFile = uploadedFilesCache.find(f => f.name === cand.filename);
                    
                    let actionButtonsHtml = '';
                    if (matchingRawFile) {
                        // Create transient, local object resource pointers
                        const fileObjectUrl = URL.createObjectURL(matchingRawFile);
                        
                        actionButtonsHtml = `
                            <div class="action-group">
                                <a href="${fileObjectUrl}" target="_blank" class="btn-action btn-view">
                                    👁️ View Resume
                                </a>
                                <a href="${fileObjectUrl}" download="${cand.filename}" class="btn-action btn-download">
                                    📥 Download File
                                </a>
                            </div>
                        `;
                    } else {
                        actionButtonsHtml = `<div class="action-group"><span style="font-size:12px; color:#94a3b8;">Original document contextual link lost</span></div>`;
                    }

                    const div = document.createElement('div');
                    div.className = 'candidate-card';
                    div.innerHTML = `
                        <div class="cand-header">
                            <span class="cand-name">${cand.name}</span>
                            <span class="score-badge">Match: ${cand.score}%</span>
                        </div>
                        <div class="meta-grid">
                            <span><strong>Education:</strong> ${cand.education}</span>
                            <span><strong>Experience:</strong> ${cand.experience} Yrs</span>
                            <span><strong>Target Universities:</strong> ${cand.universities.length > 0 ? cand.universities.join(', ') : 'None'}</span>
                            <span><strong>Document:</strong> ${cand.filename}</span>
                        </div>
                        <div class="justification-box">
                            <strong>AI Justification:</strong> ${cand.justification}
                        </div>
                        ${actionButtonsHtml}
                    `;
                    candidatesList.appendChild(div);
                });
            }
            results.classList.remove('hidden');
        } else {
            alert('Error processing data: ' + (data.error || 'Unknown application error occurred.'));
        }
    } catch (err) {
        console.error(err);
        alert('Could not establish data link connection with the Flask system engine backend.');
    } finally {
        loading.classList.add('hidden');
    }
});