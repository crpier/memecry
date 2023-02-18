function closeLoginModal() {
    var container = document.getElementById("login-modal")
    setTimeout(function () {
        container.innerHTML = ""
    }, 50)
}

function closeSignupModal() {
    var container = document.getElementById("signup-modal")
    setTimeout(function () {
        container.innerHTML = ""
    }, 50)
}

function closeUploadModal() {
    var container = document.getElementById("upload-modal")
    setTimeout(function () {
        container.innerHTML = ""
    }, 50)
}
