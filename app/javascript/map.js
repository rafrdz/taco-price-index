document.addEventListener('turbo:load', function() {
  if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
    console.error('Google Maps API is not loaded');
    return;
  }

  const map = new google.maps.Map(document.getElementById('map'), {
    zoom: 12,
    center: { lat: 29.4241, lng: -98.4936 }, // San Antonio coordinates
    mapTypeId: 'roadmap'
  });

  // Add markers for each restaurant
  const markers = [];
  const restaurantList = document.getElementById('restaurant-list');
  
  restaurantList.querySelectorAll('.list-group-item').forEach((listItem, index) => {
    const restaurantName = listItem.querySelector('h5').textContent;
    const lat = parseFloat(listItem.dataset.lat);
    const lng = parseFloat(listItem.dataset.lng);

    const marker = new google.maps.Marker({
      position: { lat, lng },
      map: map,
      title: restaurantName,
      animation: google.maps.Animation.DROP
    });

    markers.push(marker);

    // Add click event to list item
    listItem.addEventListener('click', () => {
      marker.setAnimation(google.maps.Animation.BOUNCE);
      setTimeout(() => marker.setAnimation(null), 1400);
    });

    // Add click event to marker
    marker.addListener('click', () => {
      listItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
      marker.setAnimation(google.maps.Animation.BOUNCE);
      setTimeout(() => marker.setAnimation(null), 1400);
    });
  });

  // Add search box functionality
  const searchBox = new google.maps.places.SearchBox(document.getElementById('search-box'));
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(searchBox);

  searchBox.addListener('places_changed', () => {
    const places = searchBox.getPlaces();
    if (places.length === 0) return;

    // Clear existing markers
    markers.forEach(marker => marker.setMap(null));

    // Create new marker for the selected place
    const place = places[0];
    const marker = new google.maps.Marker({
      map: map,
      position: place.geometry.location,
      title: place.name
    });

    markers.push(marker);
    map.setCenter(place.geometry.location);
    map.setZoom(15);
  });
});
