var jwt_token = localStorage.getItem('access_token');

function checkAuth() {
    fetch("/auth", {
      method: "GET",
          headers: new Headers({'Authorization':'Bearer ' + jwt_token}),
      })
      .then(response => response.json())
      .catch(error => {
        console.log(error)
        jwt_token = null;
        localStorage.removeItem('access_token');
        alert("Auth has expired. Please login again")
        window.location.href = "/static/login.html";
    })
}

function logout(){
    jwt_token = null;
    localStorage.removeItem('access_token');
    window.location.href = "/";
}

function ensureAuth() {
    setInterval(function() {
        console.log(jwt_token + " checking status")
        if (jwt_token == 'undefined') {
            jwt_token = null;
        }
        if (jwt_token) {
            checkAuth();
        }
        else{
            localStorage.removeItem('access_token');
            alert("Please login again")
            window.location.href = "/static/login.html";
        }
        toggle_signed_in_visibility();
    }, 5000);
}

function toggle_signed_in_visibility() {
    if (jwt_token) {
        document.getElementById('sign-on-up').style.visibility = "hidden";
        document.getElementById('log-on-in').style.visibility = "hidden";
        document.getElementById('log-on-out').style.visibility = "visible";
    } else {
        document.getElementById('sign-on-up').style.visibility = "visible";
        document.getElementById('log-on-in').style.visibility = "visible";
        document.getElementById('log-on-out').style.visibility = "hidden";
    }
}
window.onload = () => {
    toggle_signed_in_visibility();
}
