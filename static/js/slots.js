const form = document.querySelector('form');
const modal = document.getElementById('slots-modal');
const newSlotButton = document.getElementById('new-slot');
const closeModalBtn = document.getElementById('close-modal');
const messageSpan = document.querySelector('#slots-modal span');

newSlotButton.addEventListener('click', () => {
    modal.classList.toggle('hidden');
    modal.classList.toggle('flex');
});

closeModalBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
});

const deleteSlot = (slot, event) =>{
    event.stopPropagation();
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    if (confirm('Are you sure you want to delete this slot?')) {
        axios.delete(`/slot/${slot}`,{
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            alert(response.data.message);
            const row = document.querySelector(`tr[data-slot-id="${slot}"]`);
            if (row) {
                row.remove();
            }
            })
            .catch(error => {
                console.error('Error deleting slot:', error.response.data);
                alert('Error deleting slot. Please try again.');
        });
    }
}

let currentPage = 1;
let totalPages = 1;

const fetchSlots = (page) => {
    if (page < 1 || page > totalPages) return;

    fetch(`/slots?page=${page}`)
        .then(response => response.text())
        .then(html => {
            document.querySelector("#table-body").innerHTML = 
                new DOMParser().parseFromString(html, "text/html").querySelector("#table-body").innerHTML;
            
            document.querySelectorAll(".date-time").forEach(el => {
                const isoDate = el.dataset.datetime;
                const date = new Date(isoDate);
                const formattedTime = date.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" }).replace(":", "") + "HR";
                const formattedDate = `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`;
                const dateSpan = el.querySelector(".formatted-date");
                if (dateSpan) {
                    dateSpan.textContent = `${formattedTime} ${formattedDate}`;
                }
            });

            currentPage = page;
            totalPages = parseInt(document.querySelector("#total-pages").textContent) || 1;
            document.querySelector("#page-info").textContent = `Page ${currentPage} of ${totalPages}`;
        })
        .catch(error => console.error("Error fetching slots:", error));
};

document.addEventListener("DOMContentLoaded", () => {
    fetchSlots(currentPage);
});
