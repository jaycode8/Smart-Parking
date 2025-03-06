const form = document.querySelector('form');
const messageBox = document.querySelector('#alert-message');
const messageSpan = document.querySelector('#message-span');

document.addEventListener('DOMContentLoaded', function () {

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = {
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
        };
        messageSpan.textContent = '';

        axios.post('/signin', formData,{
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => {
                console.log(response.data)
                messageSpan.textContent = response.data.message;
                messageBox.classList.add('flex');
                messageBox.classList.remove('hidden');
                if(response.data.success){
                    messageBox.classList.add('bg-green-800');
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1500);
                    return
                }
                messageBox.classList.add('bg-red-500');
            })
            .catch(error => {
                console.error('Error creating user:', error);
                messageSpan.textContent = 'Error creating user. Please try again.';
                messageSpan.classList.add('bg-red-500');
            });
    });
});
