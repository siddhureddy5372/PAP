
function sendLocationP() {
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var latitude = position.coords.latitude;
            var longitude = position.coords.longitude;
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/location/", true); 
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.setRequestHeader("X-CSRFToken", csrfToken);
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        location.reload();
                        // Handle success response if needed
                    } else {
                        console.error('Error:', xhr.status);
                        // Handle error response if needed
                    }
                }
            };
            xhr.send("latitude=" + encodeURIComponent(latitude) + "&longitude=" + encodeURIComponent(longitude));
        });
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}
