const form = document.querySelector('form');
const modal = document.getElementById('user-modal');
const newUserButton = document.getElementById('new-user');
const closeModalBtn = document.getElementById('close-modal');
const messageSpan = document.querySelector('#user-modal span');

document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('table-body');

    newUserButton.addEventListener('click', () => {
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
            firstName: document.getElementById('firstName').value,
            lastName: document.getElementById('lastName').value,
            username: document.getElementById('username').value,
            idNo: document.getElementById('idNo').value,
            phone: document.getElementById('phone').value,
            email: document.getElementById('email').value,
            gender: document.getElementById('gender').value,
            password: document.getElementById('password').value,
        };
        messageSpan.textContent = '';

        axios.post('/users', formData)
            .then(response => {
                messageSpan.textContent = response.data.message;
                if(response.data.success){
                    messageSpan.classList.add('bg-green-500');
                    setTimeout(() => {
                        modal.classList.add('hidden');
                        modal.classList.remove('flex');
                        window.location.reload();
                    }, 1500);
                    return
                }
                messageSpan.classList.add('bg-red-500');
            })
            .catch(error => {
                console.error('Error creating user:', error.response.data);
                messageSpan.textContent = 'Error creating user. Please try again.';
                messageSpan.classList.add('bg-red-500');
            });
    });
});

const deleteUser = (userId) =>{
    if (confirm('Are you sure you want to delete this user?')) {
        axios.delete(`/user/${userId}`)
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

const editUser = async(userId) =>{
    try{
        const res = await axios.get(`/user/${userId}`)
        const userDetails = res.data.data
        modal.classList.toggle('hidden');
        modal.classList.toggle('flex');
        document.getElementById('firstName').value = userDetails.firstName
        document.getElementById('lastName').value = userDetails.lastName
        document.getElementById('username').value = userDetails.username
        document.getElementById('idNo').value = userDetails.idNo
        document.getElementById('phone').value = userDetails.phone
        document.getElementById('email').value = userDetails.email
        let genderSelect = document.getElementById('gender');
        genderSelect.value = userDetails.gender;

        form.onsubmit = async (e) => {
            e.preventDefault();

            const updatedData = {
                firstName: document.getElementById('firstName').value,
                lastName: document.getElementById('lastName').value,
                username: document.getElementById('username').value,
                idNo: document.getElementById('idNo').value,
                phone: document.getElementById('phone').value,
                email: document.getElementById('email').value,
                gender: document.getElementById('gender').value,
            };
            const password = document.getElementById('password').value
            if(password){
                updatedData["password"] = password
            }

            try {
                const res = await axios.put(`/user/${userId}`, updatedData);
                messageSpan.textContent = '';
                messageSpan.textContent = res.data.message;
                if(res.data.success){
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
                messageSpan.textContent = 'Error updating user. Please try again.'
            }
        };
    }catch(error){
        console.log(error)
    }
}