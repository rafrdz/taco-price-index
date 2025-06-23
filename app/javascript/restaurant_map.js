document.addEventListener('turbo:load', function() {
  if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
    console.error('Google Maps API is not loaded');
    return;
  }

  const map = new google.maps.Map(document.getElementById('restaurant-map'), {
    zoom: 15,
    center: { lat: parseFloat(document.getElementById('restaurant-map').dataset.lat),
              lng: parseFloat(document.getElementById('restaurant-map').dataset.lng) },
    mapTypeId: 'roadmap'
  });

  // Add marker for the restaurant
  const marker = new google.maps.Marker({
    position: map.getCenter(),
    map: map,
    title: document.getElementById('restaurant-name').textContent
  });

  // Add click event to marker
  marker.addListener('click', () => {
    marker.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(() => marker.setAnimation(null), 1400);
  });

  // Add info window
  const infoWindow = new google.maps.InfoWindow({
    content: `
      <div class="info-window">
        <h3>${marker.getTitle()}</h3>
        <p>${document.getElementById('restaurant-address').textContent}</p>
      </div>
    `
  });

  marker.addListener('click', () => {
    infoWindow.open(map, marker);
  });

  // Add street view functionality
  const streetViewControl = document.getElementById('street-view-control');
  if (streetViewControl) {
    streetViewControl.addEventListener('click', () => {
      const panorama = new google.maps.StreetViewPanorama(
        document.getElementById('street-view'),
        {
          position: map.getCenter(),
          pov: {
            heading: 34,
            pitch: 10
          }
        }
      );
      map.setStreetView(panorama);
    });
  }
});
