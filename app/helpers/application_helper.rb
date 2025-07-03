module ApplicationHelper
  # Safely renders a URL for use in link_to, preventing XSS attacks
  # Returns nil if the URL is invalid or potentially dangerous
  def safe_url(url)
    return nil if url.blank?

    # Remove any leading/trailing whitespace
    url = url.strip

    # Check if URL starts with a dangerous scheme
    return nil if url.match?(%r{\A(javascript|data|vbscript|file):|ftp://}i)

    # Ensure the URL starts with http:// or https://
    unless url.match?(%r{\Ahttps?://})
      url = "http://#{url}"
    end

    # Parse and validate the URL
    uri = URI.parse(url)

    # Only allow http and https schemes
    return nil unless %w[http https].include?(uri.scheme&.downcase)

    # Ensure the host is present and valid
    return nil if uri.host.blank?

    # Return the normalized URL
    uri.to_s
  rescue URI::InvalidURIError
    nil
  end

  # Safely renders the hostname for display, preventing XSS attacks
  def safe_hostname(url)
    return nil if url.blank?

    safe_url_value = safe_url(url)
    return nil if safe_url_value.nil?

    URI.parse(safe_url_value).host
  rescue URI::InvalidURIError
    nil
  end
end
