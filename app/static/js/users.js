
const modal = document.getElementById('user-modal');
const newUserButton = document.getElementById('new-user');
const closeModalBtn = document.getElementById('close-modal');

newUserButton.addEventListener('click', () => {
    modal.classList.toggle('hidden');
    modal.classList.toggle('flex');
});

closeModalBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
});


// const form = document.querySelector('form');

// form.addEventListener('submit', async (event) => {
//     event.preventDefault();

//     const formData = new FormData(form);

//     const data = {
//         full_name: formData.get('full_name'),
//         username: formData.get('username'),
//         id_no: formData.get('id_no'),
//         phone: formData.get('phone'),
//         email: formData.get('email'),
//         role: document.getElementById("role").value,
//         gender: document.getElementById("gender").value,
//         password: formData.get('password'),
//         is_active: true
//     };

//     try {
//         const response = await fetch('/users', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify(data),
//         });

//         const result = await response.json();

//         if (result === "success") {
//             window.location.reload();
//         } else {
//             alert("Something went wrong. Please try again.");
//         }
//     } catch (error) {
//         console.error("Error:", error);
//         alert("An error occurred while submitting the form.");
//     }
// });

