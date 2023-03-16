const instructionList = document.getElementById('instruction-list');
const infoButton = document.getElementById('info-button');
const infoDialogue = document.getElementById('info-dialogue');
infoButton.addEventListener('click', () => {
    infoDialogue.style.visibility = 'visible';
    console.log('info clcked')
})