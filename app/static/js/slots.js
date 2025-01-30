
const modal = document.getElementById('slots-modal');
const newUserButton = document.getElementById('new-slot');
const closeModalBtn = document.getElementById('close-modal');

newUserButton.addEventListener('click', () => {
    modal.classList.toggle('hidden');
    modal.classList.toggle('flex');
});

closeModalBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
});
