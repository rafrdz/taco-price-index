require "test_helper"

class FrontendPagesControllerTest < ActionDispatch::IntegrationTest
  test "should get map" do
    get frontend_pages_map_url
    assert_response :success
  end

  test "should get restaurant_details" do
    get frontend_pages_restaurant_details_url
    assert_response :success
  end

  test "should get restaurant_review_form" do
    get frontend_pages_restaurant_review_form_url
    assert_response :success
  end

  test "should get user_profile" do
    get frontend_pages_user_profile_url
    assert_response :success
  end

  test "should get featured_spotlight" do
    get frontend_pages_featured_spotlight_url
    assert_response :success
  end

  test "should get restaurant_leaderboard" do
    get frontend_pages_restaurant_leaderboard_url
    assert_response :success
  end

  test "should get catering_bulk_order" do
    get frontend_pages_catering_bulk_order_url
    assert_response :success
  end
end
