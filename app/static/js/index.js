// Toggle Modal
const modal = document.getElementById('crud-modal');
const manualAssignBtn = document.getElementById('manual-assign');
const closeModalBtn = document.getElementById('close-modal');

manualAssignBtn.addEventListener('click', () => {
    modal.classList.toggle('hidden');
    modal.classList.toggle('flex');
});

closeModalBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
});

// Webcam Handling
const webcamContainer = document.getElementById('webcam-container');
const webcamVideo = document.getElementById('webcam');
const noFeedMessage = document.getElementById('no-feed-message');

// navigator.mediaDevices.getUserMedia({ video: true })
//     .then((stream) => {
//         // Hide the message and show the video
//         noFeedMessage.style.display = 'none';
//         webcamVideo.style.display = 'block';
//         webcamVideo.srcObject = stream;
//     })
//     .catch(() => {
//         // Show fallback message
//         noFeedMessage.style.display = 'block';
//         webcamVideo.style.display = 'none';
//     });