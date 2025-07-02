require "test_helper"

class ApplicationHelperTest < ActionView::TestCase
  test "safe_url returns nil for blank URLs" do
    assert_nil safe_url("")
    assert_nil safe_url("   ")
    assert_nil safe_url(nil)
  end

  test "safe_url normalizes URLs without scheme" do
    assert_equal "http://example.com", safe_url("example.com")
    assert_equal "http://www.example.com", safe_url("www.example.com")
  end

  test "safe_url preserves valid URLs with scheme" do
    assert_equal "https://example.com", safe_url("https://example.com")
    assert_equal "http://example.com", safe_url("http://example.com")
  end

  test "safe_url rejects invalid schemes" do
    assert_nil safe_url("javascript:alert('xss')")
    assert_nil safe_url("data:text/html,<script>alert('xss')</script>")
    assert_nil safe_url("ftp://example.com")
  end

  test "safe_url handles malformed URLs" do
    assert_nil safe_url("not a url")
    assert_nil safe_url("http://")
    assert_nil safe_url("https://")
  end

  test "safe_hostname returns correct hostname" do
    assert_equal "example.com", safe_hostname("https://example.com")
    assert_equal "www.example.com", safe_hostname("www.example.com")
    assert_nil safe_hostname("javascript:alert('xss')")
    assert_nil safe_hostname("")
  end
end
