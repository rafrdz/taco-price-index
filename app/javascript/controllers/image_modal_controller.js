import { Controller } from "@hotwired/stimulus"

// Displays clicked thumbnail in a bootstrap modal and allows prev/next navigation
export default class extends Controller {
  static targets = ["img", "prevBtn", "nextBtn"]

  connect() {
    this.images = []
    this.index = 0
  }

  // Called when a thumbnail is clicked
  open(event) {
    event.preventDefault()
    const thumb = event.currentTarget
    const reviewId = thumb.dataset.reviewId
    // Collect all thumbnails that share the same review id so we can navigate
    const thumbs = document.querySelectorAll(`img[data-review-id='${reviewId}']`)
    this.images = Array.from(thumbs).map(el => el.src)
    this.index = parseInt(thumb.dataset.index || 0)
    this.showImage()

    const modalEl = this.element
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl)
    modal.show()
  }

  next() {
    if (this.images.length === 0) return
    this.index = (this.index + 1) % this.images.length
    this.showImage()
  }

  prev() {
    if (this.images.length === 0) return
    this.index = (this.index - 1 + this.images.length) % this.images.length
    this.showImage()
  }

  showImage() {
    this.imgTarget.src = this.images[this.index]
    // hide arrows if only one image
    const showArrows = this.images.length > 1
    this.prevBtnTarget.classList.toggle("d-none", !showArrows)
    this.nextBtnTarget.classList.toggle("d-none", !showArrows)
  }
}
