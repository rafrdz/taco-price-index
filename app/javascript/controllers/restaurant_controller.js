import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["favorite"]

  toggleFavorite(event) {
    event.preventDefault()
    const restaurantId = this.favoriteTarget.dataset.restaurantId
    const isFavorite = this.favoriteTarget.classList.contains('active')

    this.element.reflex("RestaurantReflex#toggle_favorite", {
      restaurantId: restaurantId,
      isFavorite: isFavorite
    })
  }
}
