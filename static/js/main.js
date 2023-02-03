console.log('script is linked');
const btnAddEntry = document.getElementById('add-entry');
const addEntryDialogue = document.getElementById('add-entry-dialogue');
btnAddEntry.addEventListener('click', () => {
    addEntryDialogue.classList.add('show');
});

const btnCloseEntry = document.getElementById('entry-x-mark');
btnCloseEntry.addEventListener('click', () => {
    addEntryDialogue.classList.remove('show');
})


const updateDialogue = document.getElementById('update-dialogue');
btnUpdate = document.getElementById('btn-update');

btnUpdate.addEventListener('click', () => {
    updateDialogue.classList.add('show');
})

function myFunction() {
    var x = document.getElementById("myTopnav");
    if (x.className === "topnav") {
      x.className += " responsive";
    } else {
      x.className = "topnav";
    }
  }

document.querySelectorAll(".drop-zone__input").forEach(inputElement => {
    const dropZoneElement = inputElement.closest(".drop-zone"); //start at input field and go up until it finds drop-zone

    dropZoneElement.addEventListener("click", e => {
        inputElement.click();
    });

    inputElement.addEventListener("change", e => {
        if (inputElement.files.length) {
            updateThumbnail(dropZoneElement, inputElement.files[0]);
        }
    });

    dropZoneElement.addEventListener("dragover", e => {
        e.preventDefault(); //prevents browser from opening the file in a new tab
        dropZoneElement.classList.add("drop-zone--over");
    });

    ["dragleave", "dragend"].forEach(type => { //dragleave when you drag out of the box, dragend when you cancel the drag with esc or something
        dropZoneElement.addEventListener(type, e => {
            dropZoneElement.classList.remove('drop-zone--over');
        });
    });

    dropZoneElement.addEventListener("drop", e => {
        e.preventDefault();

        if (e.dataTransfer.files.length) {
            inputElement.files = e.dataTransfer.files;
            updateThumbnail(dropZoneElement, e.dataTransfer.files[0]);
        }

        dropZoneElement.classList.remove("drop-zone--over");
    });
});






/**
 * Updates the thumbnail on a drop zone element.
 * 
 * @param {HTMLElement} dropZoneElement
 * @param {File} file
 */

function updateThumbnail(dropZoneElement, file){
    let thumbnailElement = dropZoneElement.querySelector(".drop-zone__thumb");
    
    console.log(file.type);

    // First time - remove the prompt
    if (dropZoneElement.querySelector(".drop-zone__prompt")) {
        dropZoneElement.querySelector(".drop-zone__prompt").remove();
    }
    //First time - there is no thumbnail element, so create
    if (!thumbnailElement) {
        thumbnailElement = document.createElement("div");
        thumbnailElement.classList.add("drop-zone__thumb");
        dropZoneElement.appendChild(thumbnailElement);
    }

    thumbnailElement.dataset.label = file.name;
    
    if (file.type === ("text/csv")) {
        console.log(file.type);
        thumbnailElement.style.backgroundImage = "url('images/csvIcon.jpg')";
        dropZoneElement.style.borderColor = "var(--border-color1)";
    } else {
        thumbnailElement.style.backgroundImage = "url('images/wrongIcon.jpg')";
        dropZoneElement.style.borderColor = "var(--error-color)";
    }
}


