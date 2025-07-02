require "test_helper"

class RestaurantShowIntegrationTest < ActionDispatch::IntegrationTest
  fixtures :restaurants

  test "restaurant show page handles safe website URLs" do
    # Create a restaurant with a valid website
    restaurant = restaurants(:one)
    restaurant.update!(website: "https://example.com")

    get restaurant_path(restaurant)
    assert_response :success

    # Should contain the safe URL
    assert_select 'a[href="https://example.com"]', text: "example.com"
  end

  test "restaurant show page handles URLs without scheme" do
    # Create a restaurant with a website without scheme
    restaurant = restaurants(:one)
    restaurant.update!(website: "http://www.example.com")

    get restaurant_path(restaurant)
    assert_response :success

    # Should contain the normalized URL with http scheme
    assert_select 'a[href="http://www.example.com"]', text: "www.example.com"
  end

  test "restaurant show page handles invalid website URLs gracefully" do
    # Create a restaurant with an invalid/dangerous website
    restaurant = restaurants(:one)
    assert_raises(ActiveRecord::RecordInvalid) do
      restaurant.update!(website: "javascript:alert('xss')")
    end
  end

  test "restaurant show page shows 'No website' when website is blank" do
    # Create a restaurant without a website
    restaurant = restaurants(:one)
    restaurant.update!(website: "")

    get restaurant_path(restaurant)
    assert_response :success

    # Should show "No website" text
    assert_match(/No website/, response.body)
  end
end
