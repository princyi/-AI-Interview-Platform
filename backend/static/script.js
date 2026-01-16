// Global variables
let currentSessionId = null;
let currentQuestions = [];
let currentQuestionIndex = 0;
let isRecording = false;
let isAnswering = false;
let mediaRecorder = null;
let audioChunks = [];
let resumeText = '';
let jobDescriptionText = '';
let silenceTimer = null;
let answerStartTime = null;
let currentAudio = null; // Track current audio playback
let recognition = null; // Web Speech Recognition
let isListening = false;

// DOM loaded event
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Interview Platform loaded');
    
    // Initialize Web Speech Recognition
    initializeSpeechRecognition();
    
    // Check microphone permissions
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            // Permission granted, close the stream
            stream.getTracks().forEach(track => track.stop());
            console.log('✅ Microphone access granted');
        })
        .catch(error => {
            console.warn('❌ Microphone access denied:', error);
            showStatus('⚠️ Please allow microphone access for voice recording to work properly.', 'error');
        });
});

// Initialize Web Speech Recognition
function initializeSpeechRecognition() {
    // Check if browser supports Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        console.error('Speech Recognition not supported');
        showStatus('❌ Speech Recognition not supported in this browser. Please use Chrome or Edge.', 'error');
        return;
    }
    
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;
    
    let finalTranscript = '';
    let isProcessing = false;
    
    recognition.onstart = function() {
        console.log('Speech recognition started');
        isListening = true;
        isProcessing = false;
        finalTranscript = '';
        document.getElementById('startAnswerBtn').classList.add('hidden');
        document.getElementById('endAnswerBtn').classList.remove('hidden');
        document.getElementById('answerStatus').textContent = '🎤 Listening... Speak your answer now';
        document.getElementById('answerStatus').className = 'status-message status-success';
    };
    
    recognition.onresult = function(event) {
        if (isProcessing) return;
        
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Update the answer text area with final + interim results
        const answerTextArea = document.getElementById('answerText');
        answerTextArea.value = finalTranscript + interimTranscript;
        
        // Reset silence timer when user speaks
        resetSilenceTimer();
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        if (event.error !== 'no-speech') {
            showStatus(`❌ Speech recognition error: ${event.error}`, 'error');
        }
        stopListening();
    };
    
    recognition.onend = function() {
        console.log('Speech recognition ended');
        isListening = false;
        if (isAnswering && finalTranscript.trim()) {
            // Update final answer
            document.getElementById('answerText').value = finalTranscript.trim();
            showStatus('✅ Answer recorded successfully!', 'success');
        }
    };
}

// Navigation functions
function nextStep(stepNumber) {
    // Hide all steps
    document.querySelectorAll('.step-container').forEach(step => {
        step.classList.add('hidden');
        step.classList.remove('active');
    });
    
    // Show target step
    const targetStep = document.getElementById(`step${stepNumber}`);
    targetStep.classList.remove('hidden');
    setTimeout(() => {
        targetStep.classList.add('active');
    }, 100);
}

function previousStep(stepNumber) {
    nextStep(stepNumber);
}

// File upload handling
async function handleFileUpload(type, input) {
    const file = input.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showStatus('Uploading file...', 'info');
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            if (type === 'resume') {
                resumeText = result.text;
                document.getElementById('resumeUploadText').innerHTML = 
                    `<i class="fas fa-check-circle"></i><br>Resume uploaded successfully`;
            } else if (type === 'job') {
                jobDescriptionText = result.text;
                document.getElementById('jobUploadText').innerHTML = 
                    `<i class="fas fa-check-circle"></i><br>Job description uploaded successfully`;
            }
            showStatus('File uploaded successfully!', 'success');
        } else {
            showStatus(`Upload failed: ${result.error}`, 'error');
        }
    } catch (error) {
        showStatus(`Upload error: ${error.message}`, 'error');
    }
}

// Generate questions using AI
async function generateQuestions() {
    const candidateName = document.getElementById('candidateName').value;
    const jobTitle = document.getElementById('jobTitle').value;
    const experienceLevel = document.getElementById('experienceLevel').value;
    const manualJobDesc = document.getElementById('jobDescriptionText').value;
    
    if (!candidateName || !jobTitle) {
        showStatus('Please fill in candidate name and job title', 'error');
        return;
    }
    
    // Use manual job description if provided, otherwise use uploaded
    const finalJobDesc = manualJobDesc || jobDescriptionText;
    
    if (!resumeText && !finalJobDesc) {
        showStatus('Please upload resume or provide job description', 'error');
        return;
    }
    
    try {
        showStatus('Creating interview session...', 'info');
        
        // Create session
        const sessionResponse = await fetch('/api/sessions/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                candidate_name: candidateName,
                job_title: jobTitle,
                resume_text: resumeText,
                job_description: finalJobDesc
            })
        });
        
        const sessionResult = await sessionResponse.json();
        
        if (!sessionResponse.ok) {
            throw new Error(sessionResult.error);
        }
        
        currentSessionId = sessionResult.session_id;
        
        showStatus('Generating AI questions...', 'info');
        
        // Generate questions
        const questionsResponse = await fetch(`/api/sessions/${currentSessionId}/questions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                experience_level: experienceLevel
            })
        });
        
        const questionsResult = await questionsResponse.json();
        
        if (!questionsResponse.ok) {
            throw new Error(questionsResult.error);
        }
        
        currentQuestions = questionsResult.questions;
        showStatus('Questions generated successfully! Starting interview...', 'success');
        
        // Skip step 3 and go directly to interview after generating questions
        setTimeout(() => {
            startInterviewAutomatically();
        }, 2000);
        
    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
    }
}

// Display generated questions
function displayQuestions(questions) {
    const container = document.getElementById('questionsContainer');
    container.innerHTML = '';
    
    questions.forEach((q, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'question-card';
        questionDiv.innerHTML = `
            <div class="question-meta">
                <span class="question-badge badge-${q.type}">${q.type}</span>
                <span class="question-badge badge-${q.difficulty}">${q.difficulty}</span>
            </div>
            <div class="question-text">${index + 1}. ${q.question}</div>
        `;
        container.appendChild(questionDiv);
    });
}

// Start interview automatically after question generation
function startInterviewAutomatically() {
    if (currentQuestions.length === 0) {
        showStatus('No questions available', 'error');
        return;
    }
    
    currentQuestionIndex = 0;
    nextStep(4);
    displayCurrentQuestion();
    updateProgress();
    
    // Wait a bit longer before auto-playing to ensure UI is ready
    setTimeout(() => {
        playQuestion();
    }, 2000);
}

// Start interview manually (for button click)
function startInterview() {
    startInterviewAutomatically();
}

// Display current question
function displayCurrentQuestion() {
    if (currentQuestionIndex >= currentQuestions.length) {
        return;
    }
    
    const question = currentQuestions[currentQuestionIndex];
    document.getElementById('currentQuestionText').textContent = question.question;
    document.getElementById('questionType').textContent = question.type;
    document.getElementById('questionType').className = `question-badge badge-${question.type}`;
    document.getElementById('questionDifficulty').textContent = question.difficulty;
    document.getElementById('questionDifficulty').className = `question-badge badge-${question.difficulty}`;
    
    // Clear previous answer and reset UI
    document.getElementById('answerText').value = '';
    isAnswering = false;
    isListening = false;
    
    // Reset button states
    document.getElementById('startAnswerBtn').classList.remove('hidden');
    document.getElementById('endAnswerBtn').classList.add('hidden');
    document.getElementById('nextQuestionBtn').classList.add('hidden');
    document.getElementById('answerStatus').classList.remove('hidden');
    document.getElementById('answerStatus').textContent = '🎧 Listen to the question, then click "Start Answer" to speak your response';
    document.getElementById('answerStatus').className = 'status-message status-info';
    document.getElementById('playBtn').innerHTML = '<i class="fas fa-play"></i>';
    
    // Update question numbers
    document.getElementById('currentQuestionNum').textContent = currentQuestionIndex + 1;
    document.getElementById('totalQuestions').textContent = currentQuestions.length;
    
    // Show/hide finish button
    if (currentQuestionIndex === currentQuestions.length - 1) {
        document.getElementById('finishBtn').classList.remove('hidden');
    } else {
        document.getElementById('finishBtn').classList.add('hidden');
    }
}

// Start answering process with Web Speech Recognition
function startAnswering() {
    if (!recognition) {
        showStatus('❌ Speech Recognition not available. Please use Chrome or Edge browser.', 'error');
        return;
    }
    
    isAnswering = true;
    answerStartTime = Date.now();
    
    // Clear previous answer
    document.getElementById('answerText').value = '';
    
    // Update UI
    document.getElementById('answerStatus').textContent = '🎤 Click "Start Answer" to begin speaking...';
    document.getElementById('answerStatus').className = 'status-message status-info';
    
    // Start speech recognition
    try {
        recognition.start();
    } catch (error) {
        console.error('Speech recognition start error:', error);
        showStatus('❌ Could not start speech recognition. Please try again.', 'error');
        isAnswering = false;
    }
    
    // Start the 5-second silence timer
    startSilenceTimer();
}

// End answering process
function endAnswering() {
    if (recognition && isListening) {
        recognition.stop();
    }
    
    isAnswering = false;
    isListening = false;
    
    // Clear silence timer
    if (silenceTimer) {
        clearTimeout(silenceTimer);
        silenceTimer = null;
    }
    
    // Update UI
    document.getElementById('startAnswerBtn').classList.remove('hidden');
    document.getElementById('endAnswerBtn').classList.add('hidden');
    document.getElementById('answerStatus').textContent = '✅ Answer completed! Moving to next question...';
    document.getElementById('answerStatus').className = 'status-message status-success';
    
    // Automatically move to next question after a short delay
    setTimeout(() => {
        proceedToNext();
    }, 2000);
}

// Stop listening (internal function)
function stopListening() {
    if (recognition && isListening) {
        recognition.stop();
    }
    isListening = false;
    
    // Reset UI
    document.getElementById('startAnswerBtn').classList.remove('hidden');
    document.getElementById('endAnswerBtn').classList.add('hidden');
}

// Start silence timer
function startSilenceTimer() {
    if (silenceTimer) {
        clearTimeout(silenceTimer);
    }
    
    silenceTimer = setTimeout(() => {
        if (isAnswering) {
            showStatus('5 seconds of silence detected. Moving to next question...', 'info');
            if (isRecording) {
                stopRecording();
            }
            setTimeout(() => {
                proceedToNext();
            }, 2000);
        }
    }, 5000);
}

// Reset silence timer (call when user speaks)
function resetSilenceTimer() {
    if (isAnswering) {
        startSilenceTimer();
    }
}

// Proceed to next question or finish
function proceedToNext() {
    if (currentQuestionIndex < currentQuestions.length - 1) {
        nextQuestion();
    } else {
        finishInterview();
    }
}

// Update progress bar
function updateProgress() {
    const progress = ((currentQuestionIndex + 1) / currentQuestions.length) * 100;
    document.getElementById('progressFill').style.width = `${progress}%`;
}

// Update volume control
function updateVolume(value) {
    document.getElementById('volumeDisplay').textContent = value + '%';
    if (currentAudio) {
        currentAudio.volume = value / 100;
    }
}

// Error handling for audio permissions
window.addEventListener('error', function(e) {
    if (e.message.includes('Permission denied')) {
        showStatus('❌ Microphone permission denied. Please allow microphone access for voice recording.', 'error');
    }
});

async function processAudioRecording(audioBlob) {
    try {
        // Convert webm to wav for better compatibility
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        
        showStatus('🔄 Processing your voice...', 'info');
        
        const response = await fetch('/api/voice/speech-to-text', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.text) {
            const currentAnswer = document.getElementById('answerText').value;
            const newText = currentAnswer ? currentAnswer + ' ' + result.text : result.text;
            document.getElementById('answerText').value = newText;
            showStatus('✅ Voice converted to text successfully!', 'success');
            
            // Reset silence timer since user spoke
            resetSilenceTimer();
            
            // Show next question button
            if (currentQuestionIndex < currentQuestions.length - 1) {
                document.getElementById('nextQuestionBtn').classList.remove('hidden');
            }
        } else {
            showStatus(`❌ Could not understand speech. Please try again.`, 'error');
            console.error('Speech recognition error:', result.error);
        }
    } catch (error) {
        showStatus(`❌ Processing error: ${error.message}`, 'error');
        console.error('Audio processing error:', error);
    }
}

// Play question as speech
async function playQuestion() {
    if (currentQuestionIndex >= currentQuestions.length) return;
    
    // Stop any currently playing audio
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
    }
    
    try {
        const question = currentQuestions[currentQuestionIndex].question;
        
        showStatus('Loading question audio...', 'info');
        
        const response = await fetch('/api/voice/text-to-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: question
            })
        });
        
        if (response.ok) {
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            currentAudio = new Audio(audioUrl);
            
            // Set up audio event listeners
            currentAudio.onloadstart = () => {
                showStatus('Playing question...', 'info');
                document.getElementById('playBtn').innerHTML = '<i class="fas fa-volume-up"></i>';
            };
            
            currentAudio.onended = () => {
                showStatus('Question finished. Click "Start Answer" when ready.', 'success');
                document.getElementById('playBtn').innerHTML = '<i class="fas fa-play"></i>';
                URL.revokeObjectURL(audioUrl); // Clean up memory
                currentAudio = null;
            };
            
            currentAudio.onerror = () => {
                showStatus('Audio playback error', 'error');
                document.getElementById('playBtn').innerHTML = '<i class="fas fa-play"></i>';
                currentAudio = null;
            };
            
            // Play the audio with volume control
            const volumeValue = document.getElementById('volumeControl').value / 100;
            currentAudio.volume = volumeValue;
            await currentAudio.play();
            
        } else {
            const result = await response.json();
            showStatus(`Text-to-speech failed: ${result.error}`, 'error');
        }
    } catch (error) {
        showStatus(`Audio error: ${error.message}`, 'error');
        document.getElementById('playBtn').innerHTML = '<i class="fas fa-play"></i>';
    }
}

// Move to next question
async function nextQuestion() {
    // Clear timers
    if (silenceTimer) {
        clearTimeout(silenceTimer);
        silenceTimer = null;
    }
    
    // Stop any currently playing audio
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
    }
    
    await saveCurrentAnswer();
    currentQuestionIndex++;
    isAnswering = false;
    
    if (currentQuestionIndex < currentQuestions.length) {
        displayCurrentQuestion();
        updateProgress();
        
        // Wait longer before auto-speaking the next question
        setTimeout(() => {
            playQuestion();
        }, 2000);
    } else {
        await finishInterview();
    }
}

// Skip current question
async function skipQuestion() {
    // Clear timers
    if (silenceTimer) {
        clearTimeout(silenceTimer);
        silenceTimer = null;
    }
    
    // Save empty answer
    await saveCurrentAnswer('Skipped');
    await nextQuestion();
}

// Save current answer
async function saveCurrentAnswer(answer = null) {
    if (!currentSessionId) return;
    
    const answerText = answer || document.getElementById('answerText').value || 'No answer provided';
    const question = currentQuestions[currentQuestionIndex];
    
    try {
        await fetch(`/api/sessions/${currentSessionId}/answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question.question,
                answer: answerText,
                question_id: question.id
            })
        });
    } catch (error) {
        console.error('Error saving answer:', error);
    }
}

// Finish interview and get results
async function finishInterview() {
    try {
        showStatus('Analyzing interview performance...', 'info');
        
        const response = await fetch(`/api/sessions/${currentSessionId}/complete`, {
            method: 'POST'
        });
        
        const results = await response.json();
        
        if (response.ok) {
            displayResults(results);
            nextStep(5);
            showStatus('Interview completed!', 'success');
        } else {
            showStatus(`Analysis failed: ${results.error}`, 'error');
        }
    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
    }
}

// Display interview results
function displayResults(results) {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = `
        <div class="score-card">
            <div class="score-value">${results.overall_score}%</div>
            <div class="score-label">Overall Score</div>
        </div>
        <div class="score-card">
            <div class="score-value">${results.category_scores.technical_skills}%</div>
            <div class="score-label">Technical Skills</div>
        </div>
        <div class="score-card">
            <div class="score-value">${results.category_scores.communication}%</div>
            <div class="score-label">Communication</div>
        </div>
        <div class="score-card">
            <div class="score-value">${results.category_scores.problem_solving}%</div>
            <div class="score-label">Problem Solving</div>
        </div>
        <div class="score-card">
            <div class="score-value">${results.category_scores.cultural_fit}%</div>
            <div class="score-label">Cultural Fit</div>
        </div>
        <div class="score-card">
            <div class="score-value">${results.category_scores.experience_relevance}%</div>
            <div class="score-label">Experience Relevance</div>
        </div>
    `;
    
    // Add detailed feedback
    const feedbackDiv = document.createElement('div');
    feedbackDiv.className = 'glass-container';
    feedbackDiv.style.marginTop = '2rem';
    feedbackDiv.innerHTML = `
        <h3 style="color: white; margin-bottom: 1rem;">Detailed Feedback</h3>
        <p style="color: rgba(255,255,255,0.9); line-height: 1.6; margin-bottom: 1rem;">${results.detailed_feedback}</p>
        
        <div style="margin-bottom: 1rem;">
            <h4 style="color: white; margin-bottom: 0.5rem;">Strengths:</h4>
            <ul style="color: rgba(255,255,255,0.8);">
                ${results.strengths.map(strength => `<li>${strength}</li>`).join('')}
            </ul>
        </div>
        
        <div style="margin-bottom: 1rem;">
            <h4 style="color: white; margin-bottom: 0.5rem;">Areas for Improvement:</h4>
            <ul style="color: rgba(255,255,255,0.8);">
                ${results.areas_for_improvement.map(area => `<li>${area}</li>`).join('')}
            </ul>
        </div>
        
        <div style="text-align: center;">
            <span class="question-badge ${results.recommendation === 'hire' ? 'badge-easy' : results.recommendation === 'maybe' ? 'badge-medium' : 'badge-hard'}">
                Recommendation: ${results.recommendation.toUpperCase()}
            </span>
        </div>
    `;
    
    container.parentNode.appendChild(feedbackDiv);
}

// Start new interview
function startNewInterview() {
    // Reset all variables
    currentSessionId = null;
    currentQuestions = [];
    currentQuestionIndex = 0;
    resumeText = '';
    jobDescriptionText = '';
    isAnswering = false;
    isListening = false;
    
    // Clear timers
    if (silenceTimer) {
        clearTimeout(silenceTimer);
        silenceTimer = null;
    }
    
    // Stop any currently playing audio
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
    }
    
    // Stop speech recognition
    if (recognition && isListening) {
        recognition.stop();
    }
    
    // Clear form inputs
    document.getElementById('candidateName').value = '';
    document.getElementById('jobTitle').value = '';
    document.getElementById('resumeUploadText').innerHTML = 
        '<i class="fas fa-cloud-upload-alt"></i><br>Click to upload your resume (PDF, DOCX, TXT)';
    document.getElementById('jobUploadText').innerHTML = 
        '<i class="fas fa-cloud-upload-alt"></i><br>Click to upload job description (PDF, DOCX, TXT)';
    document.getElementById('jobDescriptionText').value = '';
    
    // Go back to step 1
    nextStep(1);
}

// Status message functions
function showStatus(message, type) {
    const statusDiv = document.getElementById('statusMessage');
    statusDiv.className = `status-message status-${type}`;
    statusDiv.textContent = message;
    statusDiv.classList.remove('hidden');
    
    // Auto-hide success and info messages
    if (type !== 'error') {
        setTimeout(() => {
            statusDiv.classList.add('hidden');
        }, 3000);
    }
}

// Update volume control
function updateVolume(value) {
    document.getElementById('volumeDisplay').textContent = value + '%';
    if (currentAudio) {
        currentAudio.volume = value / 100;
    }
}

// Error handling for audio permissions
window.addEventListener('error', function(e) {
    if (e.message.includes('Permission denied')) {
        showStatus('❌ Microphone permission denied. Please allow microphone access for voice recording.', 'error');
    }
});

// Check microphone permissions on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Interview Platform loaded');
    
    // Check microphone permissions
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            // Permission granted, close the stream
            stream.getTracks().forEach(track => track.stop());
            console.log('✅ Microphone access granted');
        })
        .catch(error => {
            console.warn('❌ Microphone access denied:', error);
            showStatus('⚠️ Please allow microphone access for voice recording to work properly.', 'error');
        });
});
