// Restaurant Filtering System
class RestaurantFilters {
  constructor() {
    this.restaurants = [];
    this.filteredRestaurants = [];
    this.activeFilters = {
      search: '',
      cuisine: '',
      openNow: false,
      distance: '',
      tags: []
    };
    
    this.init();
  }
  
  init() {
    this.cacheElements();
    this.bindEvents();
    this.loadRestaurantData();
    this.setupTags();
  }
  
  cacheElements() {
    // Filter elements
    this.searchInput = document.getElementById('searchInput');
    this.cuisineFilter = document.getElementById('cuisineFilter');
    this.openNowToggle = document.getElementById('openNowToggle');
    this.distanceFilter = document.getElementById('distanceFilter');
    this.clearFiltersBtn = document.getElementById('clearFilters');
    this.resultsCount = document.getElementById('resultsCount');
    this.tagsList = document.getElementById('tagsList');
    
    // Restaurant cards container
    this.restaurantContainer = document.querySelector('.restaurant-cards-container');
  }
  
  bindEvents() {
    // Search input - button-based search
    if (this.searchInput) {
      // Search on Enter key
      this.searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          this.performSearch();
        }
      });
      
      // Show/hide clear button based on input
      this.searchInput.addEventListener('input', (e) => {
        const clearBtn = document.getElementById('clearSearchBtn');
        if (clearBtn) {
          clearBtn.style.display = e.target.value.trim() ? 'flex' : 'none';
        }
      });
    }
    
    // Search button
    const searchBtn = document.getElementById('searchBtn');
    if (searchBtn) {
      searchBtn.addEventListener('click', () => {
        this.performSearch();
      });
    }
    
    // Clear search button
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    if (clearSearchBtn) {
      clearSearchBtn.addEventListener('click', () => {
        this.clearSearch();
      });
    }
    
    // Cuisine dropdown
    if (this.cuisineFilter) {
      this.cuisineFilter.addEventListener('change', (e) => {
        this.activeFilters.cuisine = e.target.value;
        this.filterRestaurants();
      });
    }
    
    // Open now toggle
    if (this.openNowToggle) {
      this.openNowToggle.addEventListener('change', (e) => {
        this.activeFilters.openNow = e.target.checked;
        this.filterRestaurants();
      });
    }
    
    // Distance filter
    if (this.distanceFilter) {
      this.distanceFilter.addEventListener('change', (e) => {
        this.activeFilters.distance = e.target.value;
        this.filterRestaurants();
      });
    }
    
    // Clear filters
    if (this.clearFiltersBtn) {
      this.clearFiltersBtn.addEventListener('click', () => {
        this.clearAllFilters();
      });
    }
  }
  
  setupTags() {
    if (!this.tagsList) return;
    
    const tagButtons = this.tagsList.querySelectorAll('.tag-button');
    tagButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggleTag(button);
      });
    });
  }
  
  toggleTag(button) {
    const tag = button.getAttribute('data-tag');
    const isActive = button.classList.contains('active');
    
    if (isActive) {
      // Remove tag
      button.classList.remove('active');
      const index = this.activeFilters.tags.indexOf(tag);
      if (index > -1) {
        this.activeFilters.tags.splice(index, 1);
      }
    } else {
      // Add tag
      button.classList.add('active');
      if (!this.activeFilters.tags.includes(tag)) {
        this.activeFilters.tags.push(tag);
      }
    }
    
    this.filterRestaurants();
  }
  
  loadRestaurantData() {
    // Load restaurant data from the DOM
    const restaurantCards = document.querySelectorAll('.restaurant-card');
    this.restaurants = Array.from(restaurantCards).map(card => {
      const name = card.querySelector('.restaurant-name')?.textContent || '';
      const cuisine = card.querySelector('.cuisine-type')?.textContent || '';
      const statusBadge = card.querySelector('.status-badge');
      const status = statusBadge?.textContent || '';
      const location = card.querySelector('.location-info')?.textContent || '';
      
      // Better open/closed detection using CSS class and text content
      let isOpen = false;
      if (statusBadge) {
        // Check CSS classes first (most reliable)
        if (statusBadge.classList.contains('status-open')) {
          isOpen = true;
        } else if (statusBadge.classList.contains('status-closed')) {
          isOpen = false;
        } else {
          // Fallback to text content
          const statusText = status.toLowerCase().trim();
          isOpen = statusText.includes('open now') || statusText === 'open';
        }
      }
      
      // Extract distance if available (assumes format like \"2.5 mi - City\")
      let distance = null;
      const locationMatch = location.match(/(\d+\.?\d*) mi/);
      if (locationMatch) {
        distance = parseFloat(locationMatch[1]);
      }
      
      // Get tags from data attributes
      const tags = JSON.parse(card.getAttribute('data-tags') || '[]');
      
      console.log(`Loading restaurant: ${name}, Status: '${status}', isOpen: ${isOpen}, CSS classes: ${statusBadge?.className}`);
      
      return {
        element: card,
        name: name.toLowerCase(),
        cuisine: cuisine.toLowerCase(),
        isOpen: isOpen,
        statusText: status,
        distance: distance,
        tags: tags,
        visible: true
      };
    });
    
    this.filteredRestaurants = [...this.restaurants];
    this.updateResultsCount();
  }
  
  filterRestaurants() {
    this.filteredRestaurants = this.restaurants.filter(restaurant => {
      // Search filter - only apply if there's search text, otherwise show all
      if (this.activeFilters.search && this.activeFilters.search !== '') {
        if (!restaurant.name.includes(this.activeFilters.search)) {
          return false;
        }
      }
      
      // Cuisine filter
      if (this.activeFilters.cuisine && 
          restaurant.cuisine !== this.activeFilters.cuisine.toLowerCase()) {
        return false;
      }
      
      // Open now filter - more robust checking
      if (this.activeFilters.openNow) {
        console.log(`Checking ${restaurant.name}: isOpen = ${restaurant.isOpen}, status text = '${restaurant.statusText}'`);
        if (!restaurant.isOpen) {
          return false;
        }
      }
      
      // Distance filter
      if (this.activeFilters.distance && restaurant.distance) {
        const maxDistance = parseFloat(this.activeFilters.distance);
        if (restaurant.distance > maxDistance) {
          return false;
        }
      }
      
      // Tags filter
      if (this.activeFilters.tags.length > 0) {
        const hasAllTags = this.activeFilters.tags.every(tag => 
          restaurant.tags.includes(tag)
        );
        if (!hasAllTags) {
          return false;
        }
      }
      
      return true;
    });
    
    this.renderFilteredResults();
    this.updateResultsCount();
  }
  
  renderFilteredResults() {
    // Hide all restaurants first
    this.restaurants.forEach(restaurant => {
      restaurant.element.style.display = 'none';
      restaurant.visible = false;
    });
    
    // Show filtered restaurants with animation
    this.filteredRestaurants.forEach((restaurant, index) => {
      setTimeout(() => {
        restaurant.element.style.display = 'block';
        restaurant.element.style.animation = 'fadeInUp 0.3s ease forwards';
        restaurant.visible = true;
      }, index * 50); // Stagger animation
    });
    
    // Show \"no results\" message if needed
    this.showNoResultsMessage();
  }
  
  showNoResultsMessage() {
    let noResultsMsg = document.getElementById('noResultsMessage');
    
    if (this.filteredRestaurants.length === 0) {
      if (!noResultsMsg) {
        noResultsMsg = document.createElement('div');
        noResultsMsg.id = 'noResultsMessage';
        noResultsMsg.className = 'no-results-message';
        noResultsMsg.innerHTML = `
          <div class=\"text-center py-5\">
            <i class=\"fas fa-search fa-3x text-muted mb-3\"></i>
            <h4 class=\"text-muted\">No restaurants found</h4>
            <p class=\"text-muted\">Try adjusting your filters or search terms</p>
            <button class=\"btn btn-primary\" onclick=\"restaurantFilters.clearAllFilters()\">
              Clear All Filters
            </button>
          </div>
        `;
        this.restaurantContainer.appendChild(noResultsMsg);
      }
      noResultsMsg.style.display = 'block';
    } else {
      if (noResultsMsg) {
        noResultsMsg.style.display = 'none';
      }
    }
  }
  
  updateResultsCount() {
    if (this.resultsCount) {
      this.resultsCount.textContent = this.filteredRestaurants.length;
    }
  }
  
  performSearch() {
    if (!this.searchInput) return;
    
    const searchTerm = this.searchInput.value.toLowerCase().trim();
    this.activeFilters.search = searchTerm;
    
    console.log(`Performing search for: "${searchTerm}"`);
    
    // Show/hide clear button
    const clearBtn = document.getElementById('clearSearchBtn');
    if (clearBtn) {
      clearBtn.style.display = searchTerm ? 'flex' : 'none';
    }
    
    this.filterRestaurants();
  }
  
  clearSearch() {
    if (this.searchInput) {
      this.searchInput.value = '';
    }
    
    this.activeFilters.search = '';
    
    // Hide clear button
    const clearBtn = document.getElementById('clearSearchBtn');
    if (clearBtn) {
      clearBtn.style.display = 'none';
    }
    
    console.log('Search cleared');
    
    this.filterRestaurants();
  }
  
  clearAllFilters() {
    // Reset all filter values
    this.activeFilters = {
      search: '',
      cuisine: '',
      openNow: false,
      distance: '',
      tags: []
    };
    
    // Reset UI elements
    if (this.searchInput) this.searchInput.value = '';
    if (this.cuisineFilter) this.cuisineFilter.selectedIndex = 0;
    if (this.openNowToggle) this.openNowToggle.checked = false;
    if (this.distanceFilter) this.distanceFilter.selectedIndex = 0;
    
    // Hide clear search button
    const clearBtn = document.getElementById('clearSearchBtn');
    if (clearBtn) {
      clearBtn.style.display = 'none';
    }
    
    // Reset tag buttons
    if (this.tagsList) {
      const tagButtons = this.tagsList.querySelectorAll('.tag-button');
      tagButtons.forEach(button => {
        button.classList.remove('active');
      });
    }
    
    // Show all restaurants
    this.filteredRestaurants = [...this.restaurants];
    this.renderFilteredResults();
    this.updateResultsCount();
  }
  
  // Utility function for debouncing search input
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}

// Animation CSS for fade in effect
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .no-results-message {
    grid-column: 1 / -1;
    background-color: white;
    border-radius: 15px;
    padding: 40px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    margin: 20px 0;
  }
`;
document.head.appendChild(style);

// Initialize the filter system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  window.restaurantFilters = new RestaurantFilters();
});

// Also initialize on Turbo load for Rails apps
document.addEventListener('turbo:load', function() {
  window.restaurantFilters = new RestaurantFilters();
});
