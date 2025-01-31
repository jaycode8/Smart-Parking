const form = document.querySelector('form');
const modal = document.getElementById('slots-modal');
const newSlotButton = document.getElementById('new-slot');
const closeModalBtn = document.getElementById('close-modal');
const messageSpan = document.querySelector('#slots-modal span');


document.addEventListener('DOMContentLoaded', function () {
    newSlotButton.addEventListener('click', () => {
        modal.classList.toggle('hidden');
        modal.classList.toggle('flex');
    });

    closeModalBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    });

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        const formData = {
            slotId: document.getElementById('slotId').value,
            floor: document.getElementById('floor').value,
        };
        messageSpan.textContent = '';
        axios.defaults.xsrfCookieName = 'csrftoken';
        axios.defaults.xsrfHeaderName = 'X-CSRFToken';
        axios.defaults.withCredentials = true;
        try {
            const response = axios.post('/slots', formData);
            messageSpan.textContent = response.data.message;

            if (response.data.success) {
                messageSpan.classList.add('bg-green-500');
                setTimeout(() => {
                    modal.classList.add('hidden');
                    modal.classList.remove('flex');
                    window.location.reload();
                }, 1500);
                return
            }
            messageSpan.classList.add('bg-red-500');

        } catch (error) {
            console.error('Error creating slot:', error.response);
            messageSpan.textContent = 'Error creating slot. Please try again.';
            messageSpan.classList.add('bg-red-500');
        }
    });

})

const editSlot = async (id) => {
    try {
        const res = await axios.get(`/slot/${id}`)
        const slotDetails = res.data.data
        modal.classList.toggle('hidden');
        modal.classList.toggle('flex');
        document.getElementById('slotId').value = slotDetails.slotId
        let floorSelect = document.getElementById('floor');
        floorSelect.value = slotDetails.floor;

        form.onsubmit = async (e) => {
            e.preventDefault();

            const updatedData = {
                slotId: document.getElementById('slotId').value,
                floor: document.getElementById('floor').value,
            };

            try {
                const res = await axios.put(`/slot/${id}`, updatedData);
                messageSpan.textContent = '';
                messageSpan.textContent = res.data.message;
                if (res.data.success) {
                    messageSpan.classList.add('bg-green-500');
                    setTimeout(() => {
                        modal.classList.add('hidden');
                        modal.classList.remove('flex');
                        window.location.reload();
                    }, 1500);
                    return
                }
                messageSpan.classList.add('bg-red-500');
            } catch (error) {
                messageSpan.classList.add('bg-red-500');
                messageSpan.textContent = 'Error updating parking slot. Please try again.'
            }
        };
    } catch (error) {
        console.log(error)
    }
}
