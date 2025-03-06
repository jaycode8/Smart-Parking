const form = document.querySelector('form');
const modal = document.getElementById('user-modal');
const newUserButton = document.getElementById('new-user');
const closeModalBtn = document.getElementById('close-modal');
const messageSpan = document.querySelector('#user-modal span');
const token = localStorage.getItem('smartPToken');

const tableBody = document.getElementById('table-body');

newUserButton.addEventListener('click', () => {
    modal.classList.toggle('hidden');
    modal.classList.toggle('flex');
});

closeModalBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
});

const deleteUser = (userId, event) => {
    event.stopPropagation();
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    if (confirm('Are you sure you want to delete this user?')) {
        axios.delete(`/user/${userId}`,{
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => {
                console.log('User deleted successfully:', response.data);
                const row = document.querySelector(`tr[data-user-id="${userId}"]`);
                if (row) {
                    row.remove();
                }
            })
            .catch(error => {
                console.error('Error deleting user:', error.response.data);
                alert('Error deleting user. Please try again.');
            });
    }
}

let currentPage = 1;
let totalPages = 1;

const fetchUsers = (page) => {
    if (page < 1 || page > totalPages) return;

    fetch(`/users?page=${page}`)
        .then(response => response.text())
        .then(html => {
            document.querySelector("#table-body").innerHTML = 
                new DOMParser().parseFromString(html, "text/html").querySelector("#table-body").innerHTML;

            currentPage = page;
            totalPages = parseInt(document.querySelector("#total-pages").textContent) || 1;
            document.querySelector("#page-info").textContent = `Page ${currentPage} of ${totalPages}`;
        })
        .catch(error => console.error("Error fetching users:", error));
};

document.addEventListener("DOMContentLoaded", () => {
    fetchUsers(currentPage);
});