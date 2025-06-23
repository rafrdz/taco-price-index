import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  submit(event) {
    event.preventDefault()
    const form = event.target
    const formData = new FormData(form)

    fetch(`/restaurants/${formData.get('restaurant_id')}/reviews`, {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      const reviewsContainer = this.element.querySelector('#reviews-container')
      const newReview = document.createElement('div')
      newReview.innerHTML = `
        <div class="card mb-3">
          <div class="card-body">
            <h5 class="card-title">${data.title}</h5>
            <p class="card-text">${data.content}</p>
            <p class="card-text"><small class="text-muted">${data.created_at}</small></p>
          </div>
        </div>
      `
      reviewsContainer.insertBefore(newReview, reviewsContainer.firstChild)
      form.reset()
      this.element.querySelector('.review-form').reset()
    })
    .catch(error => console.error('Error:', error))
  }
}
