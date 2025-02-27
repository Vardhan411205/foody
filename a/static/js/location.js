let map;
let marker;
let userLocation = null;

// Initialize the map
function initMap() {
    map = L.map('map').setView([20.5937, 78.9629], 5); // Default center of India
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add click event to map
    map.on('click', function(e) {
        setMarker(e.latlng);
        getAddressFromLatLng(e.latlng);
    });
}

// Set marker on map
function setMarker(latlng) {
    if (marker) {
        map.removeLayer(marker);
    }
    marker = L.marker(latlng).addTo(map);
    map.setView(latlng, 16);
}

// Get address from coordinates using OpenStreetMap Nominatim
async function getAddressFromLatLng(latlng) {
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latlng.lat}&lon=${latlng.lng}`);
        const data = await response.json();
        const address = data.display_name;
        document.getElementById('selected-address').textContent = address;
        userLocation = {
            lat: latlng.lat,
            lng: latlng.lng,
            address: address
        };
    } catch (error) {
        console.error('Error getting address:', error);
    }
}

// Search location
async function searchLocation(query) {
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`);
        const data = await response.json();
        if (data.length > 0) {
            const location = data[0];
            const latlng = L.latLng(location.lat, location.lon);
            setMarker(latlng);
            getAddressFromLatLng(latlng);
        }
    } catch (error) {
        console.error('Error searching location:', error);
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('map-modal');
    const changeLocationBtn = document.getElementById('change-location');
    const closeModal = document.querySelector('.close-modal');
    const confirmBtn = document.getElementById('confirm-location');
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('location-search');
    const locationInput = document.getElementById('location-input');

    // Open modal
    changeLocationBtn.addEventListener('click', function() {
        modal.classList.add('active');
        if (!map) {
            initMap();
        }
    });

    // Close modal
    closeModal.addEventListener('click', function() {
        modal.classList.remove('active');
    });

    // Confirm location
    confirmBtn.addEventListener('click', function() {
        if (userLocation) {
            document.getElementById('current-location').textContent = userLocation.address;
            // Save location to localStorage
            localStorage.setItem('userLocation', JSON.stringify(userLocation));
            modal.classList.remove('active');
            
            // Update profile location if profile exists
            updateProfileLocation(userLocation);
        }
    });

    // Search location
    searchBtn.addEventListener('click', function() {
        const query = searchInput.value;
        if (query) {
            searchLocation(query);
        }
    });

    // Enter key in search
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = searchInput.value;
            if (query) {
                searchLocation(query);
            }
        }
    });

    // Load saved location if exists
    const savedLocation = localStorage.getItem('userLocation');
    if (savedLocation) {
        const location = JSON.parse(savedLocation);
        document.getElementById('current-location').textContent = location.address;
    }

    locationInput.addEventListener('change', function() {
        fetch('{% url "joo:update_location" %}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `location=${encodeURIComponent(this.value)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update was successful
                console.log('Location updated');
            }
        });
    });
});

// Update profile location
function updateProfileLocation(location) {
    const profileLocationElement = document.querySelector('.profile-location');
    if (profileLocationElement) {
        profileLocationElement.textContent = location.address;
    }
} 