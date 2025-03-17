const form = document.querySelector('form');
const messageBox = document.querySelector('#alert-message');
const messageSpan = document.querySelector('#message-span');

function showToast(message, clr) {
    Toastify({
        text: message,
        duration: 5000,
        close: true,
        gravity: "top",
        position: "right",
        backgroundColor: clr,
        stopOnFocus: true,
    }).showToast();
}

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
                if(response.data.success){
                    showToast(response.data.message, "#22c55e")
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1500);
                    return
                }
            })
            .catch(error => {
                showToast("Wrong username or password", "red")
            });
    });
});
