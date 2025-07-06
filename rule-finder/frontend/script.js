document.getElementById('upload-button').addEventListener('click', async () => {
    const fileInput = document.getElementById('pdf-upload');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a PDF file to upload.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://localhost:8000/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        alert(result.message || result.error);
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('An error occurred while uploading the file.');
    }
});

document.getElementById('ask-button').addEventListener('click', async () => {
    const question = document.getElementById('question-input').value;

    if (!question) {
        alert('Please enter a question.');
        return;
    }

    const formData = new FormData();
    formData.append('question', question);

    try {
        const response = await fetch('http://localhost:8000/api/ask', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (result.answer) {
            document.getElementById('answer').innerText = result.answer;
        } else {
            document.getElementById('answer').innerText = result.error;
        }
    } catch (error) {
        console.error('Error asking question:', error);
        alert('An error occurred while asking the question.');
    }
});
