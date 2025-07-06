import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["streetAddress", "city", "state", "zip", "latitude", "longitude"]
  static values = { 
    debounceMs: { type: Number, default: 1000 }
  }

  connect() {
    this.debounceTimer = null
    this.setupAddressListeners()
  }

  disconnect() {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer)
    }
  }

  setupAddressListeners() {
    // Add event listeners to address fields
    this.streetAddressTarget.addEventListener('input', () => this.debouncedGeocode())
    this.cityTarget.addEventListener('input', () => this.debouncedGeocode())
    this.stateTarget.addEventListener('input', () => this.debouncedGeocode())
    this.zipTarget.addEventListener('input', () => this.debouncedGeocode())
  }

  debouncedGeocode() {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer)
    }
    
    this.debounceTimer = setTimeout(() => {
      this.geocodeAddress()
    }, this.debounceMsValue)
  }

  async geocodeAddress() {
    const streetAddress = this.streetAddressTarget.value.trim()
    const city = this.cityTarget.value.trim()
    const state = this.stateTarget.value.trim()
    const zip = this.zipTarget.value.trim()

    // Only geocode if we have at least street address and city
    if (!streetAddress || !city) {
      console.log('Insufficient address data for geocoding')
      return
    }

    // Debug: log form state before geocoding
    this.logFormState()

    // Build the full address
    const address = [streetAddress, city, state, zip].filter(Boolean).join(', ')

    try {
      // Load Google Maps API if not already loaded
      await this.loadGoogleMapsAPI()
      
      // Create geocoder instance
      const geocoder = new google.maps.Geocoder()
      
      geocoder.geocode({ address: address }, (results, status) => {
        if (status === 'OK' && results[0]) {
          const location = results[0].geometry.location
          try {
            // Format to 6 decimal places to avoid validation issues
            const lat = location.lat().toFixed(6)
            const lng = location.lng().toFixed(6)
            
            // Validate coordinates before setting
            if (this.validateAndSetCoordinate('latitude', lat) && 
                this.validateAndSetCoordinate('longitude', lng)) {
              this.latitudeTarget.value = lat
              this.longitudeTarget.value = lng
              
              // Add visual feedback
              this.showSuccessFeedback()
            } else {
              console.error('Invalid coordinates received from geocoding')
              this.showErrorFeedback()
            }
          } catch (error) {
            console.error('Error setting coordinate values:', error)
            this.showErrorFeedback()
          }
        } else {
          console.warn('Geocoding failed:', status)
          this.showErrorFeedback()
        }
      })
    } catch (error) {
      console.error('Error during geocoding:', error)
      this.showErrorFeedback()
    }
  }

  loadGoogleMapsAPI() {
    return new Promise((resolve, reject) => {
      if (window.google && window.google.maps) {
        resolve()
        return
      }

      // Use the existing loadGoogleMapsAPI function from the layout
      if (typeof window.loadGoogleMapsAPI === 'function') {
        window.loadGoogleMapsAPI(resolve)
      } else {
        reject(new Error('Google Maps API not available'))
      }
    })
  }

  showSuccessFeedback() {
    // Add success styling to latitude/longitude fields
    this.latitudeTarget.classList.add('is-valid')
    this.longitudeTarget.classList.add('is-valid')
    
    // Remove error styling if it was there
    this.latitudeTarget.classList.remove('is-invalid')
    this.longitudeTarget.classList.remove('is-invalid')
    
    // Clear success styling after 3 seconds
    setTimeout(() => {
      this.latitudeTarget.classList.remove('is-valid')
      this.longitudeTarget.classList.remove('is-valid')
    }, 3000)
  }

  showErrorFeedback() {
    // Add error styling to latitude/longitude fields
    this.latitudeTarget.classList.add('is-invalid')
    this.longitudeTarget.classList.add('is-invalid')
    
    // Remove success styling if it was there
    this.latitudeTarget.classList.remove('is-valid')
    this.longitudeTarget.classList.remove('is-valid')
    
    // Clear error styling after 3 seconds
    setTimeout(() => {
      this.latitudeTarget.classList.remove('is-invalid')
      this.longitudeTarget.classList.remove('is-invalid')
    }, 3000)
  }

  // Method to validate coordinate values before setting them
  validateAndSetCoordinate(field, value) {
    try {
      const numValue = parseFloat(value)
      if (isNaN(numValue)) {
        console.error(`Invalid coordinate value: ${value}`)
        return false
      }
      
      // Validate latitude range (-90 to 90)
      if (field === 'latitude' && (numValue < -90 || numValue > 90)) {
        console.error(`Latitude out of range: ${numValue}`)
        return false
      }
      
      // Validate longitude range (-180 to 180)
      if (field === 'longitude' && (numValue < -180 || numValue > 180)) {
        console.error(`Longitude out of range: ${numValue}`)
        return false
      }
      
      return true
    } catch (error) {
      console.error(`Error validating coordinate: ${error}`)
      return false
    }
  }

  // Debug method to log form state
  logFormState() {
    console.log('Form state:', {
      streetAddress: this.streetAddressTarget.value,
      city: this.cityTarget.value,
      state: this.stateTarget.value,
      zip: this.zipTarget.value,
      latitude: this.latitudeTarget.value,
      longitude: this.longitudeTarget.value,
      latitudeStep: this.latitudeTarget.step,
      longitudeStep: this.longitudeTarget.step
    })
  }

  manualGeocode() {
    // Clear any existing debounce timer
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer)
    }
    
    // Immediately geocode
    this.geocodeAddress()
  }
} 