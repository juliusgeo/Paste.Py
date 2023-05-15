var editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
    lineNumbers: true,
    theme: "dracula",
    mode: "python",
    styleActiveLine: true
});

editor.on("change", function() {
    document.getElementById("snippet-input").value = editor.getValue();
});

document.getElementById('save-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const response = await fetch('/save', {
        method: 'POST',
        body: new FormData(this)
    });

    if (response.redirected) {
        // Redirect to the snippet page
        window.location.href = response.url;
    } else {
        // Handle error response
        const responseData = await response.json();
        const { error } = responseData;
        showErrorPopup(error);
    }
});

function showErrorPopup(errorMessage) {
    var errorPopup = document.getElementById("error-popup");
    var errorMessageElement = document.getElementById("error-message");
    errorMessageElement.textContent = errorMessage;
    errorPopup.style.display = "flex";
    setTimeout(function() {
        errorPopup.style.display = "none";
    }, 2000);
}

// Add an event listener for file input change
document.getElementById('file-input').addEventListener('change', function(event) {
    var file = event.target.files[0];
    if (file) {
        var reader = new FileReader();
        reader.onload = function(e) {
            editor.setValue(e.target.result);
        };
        reader.readAsText(file);
    }
});
