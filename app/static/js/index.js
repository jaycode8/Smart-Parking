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

navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
        // Hide the message and show the video
        noFeedMessage.style.display = 'none';
        webcamVideo.style.display = 'block';
        webcamVideo.srcObject = stream;

        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");

        function captureFrame() {
            canvas.width = webcamVideo.videoWidth;
            canvas.height = webcamVideo.videoHeight;
            context.drawImage(webcamVideo, 0, 0, canvas.width, canvas.height);
            
            // Convert frame to Base64
            const frameData = canvas.toDataURL("image/jpeg");

            // Send to Django backend using Axios
            axios.post("/detection", { image: frameData }, {
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": "{{ csrf_token }}"  // Ensure CSRF token is included
                }
            })
            .then(response => {
                console.log("Detected Plates:", response.data);
                // Handle detection results (display, highlight, etc.)
            })
            .catch(error => {
                console.error("Error:", error);
            });
        }

        // Capture a frame every 2 seconds
        setInterval(captureFrame, 2000);
    })
    .catch((err) => {
        console.log(err)
        // Show fallback message
        noFeedMessage.style.display = 'block';
        webcamVideo.style.display = 'none';
    });