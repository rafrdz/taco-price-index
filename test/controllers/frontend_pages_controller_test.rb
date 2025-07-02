require "test_helper"

class FrontendPagesControllerTest < ActionDispatch::IntegrationTest
  setup do
    @user = users(:one)
    sign_in_as @user
  end

  teardown do
    sign_out
  end

  test "should get map" do
    get frontend_pages_map_url
    assert_response :success
  end

  test "should get user_profile" do
    get frontend_pages_user_profile_url
    assert_response :success
  end
end
