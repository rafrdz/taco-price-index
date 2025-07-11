import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["count", "icon", "text", "button"]

  toggle(event) {
    event.preventDefault()
    const button = this.buttonTarget;
    const restaurantId = this.element.dataset.restaurantId;

    if (!restaurantId) {
      console.error("Restaurant ID is missing on the button's dataset.");
      return; // Stop execution if ID is missing
    }

    fetch(`/restaurants/${restaurantId}/toggle_favorite`, {
      method: 'POST',
      headers: {
        'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      credentials: 'same-origin'
    })
    .then(response => {
      if (response.redirected) {
        // If we get redirected, it means we need to log in
        window.location.href = response.url
        return
      }
      return response.json()
    })
    .then(data => {
      if (!data) return // Skip if we were redirected

      if(data.is_favorite) {
        button.classList.remove('btn-outline-danger'); 
        button.classList.add('btn-danger');
      } else {
        button.classList.remove('btn-danger');
        button.classList.add('btn-outline-danger');
      }

      button.innerHTML = data.is_favorite ? 'Unfavorite' : 'Favorite';
      const countElement = button.nextElementSibling;

      if (countElement && countElement.matches('[data-favorite-target="count"]')) {
        countElement.textContent = data.favorite_count;
      } else {
        console.warn('Favorite count element not found as immediate next sibling with data-favorite-target="count".');
      }
    })
    .catch(error => console.error('Error:', error))
  }
}
