document.addEventListener("DOMContentLoaded", function() {
    // Dropdown functionality
    var dropdown = document.querySelector(".dropdown-btn");
    if (dropdown) {
        dropdown.addEventListener("click", function() {
            this.classList.toggle("active");
            var dropdownContent = this.nextElementSibling;
            dropdownContent.classList.toggle("show");
        });
    }

    // Geolocation functionality
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            document.getElementById("latitude").value = position.coords.latitude;
            document.getElementById("longitude").value = position.coords.longitude;
        }, function(error) {
            console.log("Error obteniendo la ubicación: " + error.message);
        });
    } else {
        console.log("Geolocalización no soportada por este navegador.");
    }
});
