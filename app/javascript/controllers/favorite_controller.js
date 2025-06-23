import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  toggle(event) {
    event.preventDefault()
    const button = event.currentTarget
    const restaurantId = button.dataset.restaurantId

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
      
      const isFavorited = button.classList.toggle('favorited')
      button.innerHTML = isFavorited ? 'Unfavorite' : 'Favorite'
      const countElement = this.element.querySelector(`[data-restaurant-id="${restaurantId}"] .favorite-count`)
      if (countElement) {
        countElement.textContent = data.favorite_count
      }
    })
    .catch(error => console.error('Error:', error))
  }
}
