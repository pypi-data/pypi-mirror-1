var files_completed = Array();
var upload_errors = Array();
var timerID = 0;

function successful_upload() {
    with (document.forms.upload_complete) {
        portal_status_message.value = 'Files successfully uploaded';
        submit();
    }
}

/* all uploads were completed */
function z3cFlashUploadOnUploadComplete(status) {
    // for some bizarre reason IE doesn't like a form submit here immediately
    timerID = setTimeout("successful_upload()", 500);
}

/* overrides code in the z3c.widgets.flashupload that hides/disables the button */

function z3cFlashUploadDisableBrowseButton() {
}

/* an individual file has been uploaded */
function z3cFlashUploadOnFileComplete(filename) {
    files_completed.push(filename);
}

/* cancel button hit during browse dialog */
function z3cFlashUploadOnCancelEvent() {
}

/* an error occurred while trying to upload a file */
function z3cFlashUploadOnErrorEvent(error_str) {
    upload_errors.push(error_str);
    alert("Error: "+error_str);
}

function z3cFlashUploadNoFlash() {
    with (document.forms.upload_complete) {
        upload_button.disabled = true;
        upload_button.style.color = '#aaaaaa';
        upload_button.style.borderColor = '#aaaaaa';
    }
}
