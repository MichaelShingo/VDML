const instructionList = document.getElementById('instruction-list');
const infoButton = document.getElementById('info-button');
const infoDialogue = document.getElementById('info-dialogue');
infoButton.addEventListener('click', () => {
    //instructionList.classList.toggle('hide');
    //infoDialogue.classList.toggle('hide');
    infoDialogue.style.visibility = 'visible';
    console.log('info clcked')
})