function signup(){
    fetch("/signup", {
      method: "POST",
      headers: {'Content-Type': 'application/json'}, 
      body: JSON.stringify(
            {
                    "password": document.getElementById("password").value,
                    "email": document.getElementById("email").value,
            }
      )
    })
    .then((response) => {
        if (response.status == 200) {
            return response.json();
        } else {
            return null;
        }
    })
    .then((data) => {
        if (data) {
            console.log("got response: " + data.access_token)
            localStorage.setItem("access_token", data.access_token);
            jwt_token = data.access_token;
            window.location='/static/index.html'
        } else {
            // TODO no alerts
            alert("Incorrect email or password. Please try again!");
        }
    })
    .catch(error => {
        console.error(error);
        alert("There was an error please try again!");
    });
}
