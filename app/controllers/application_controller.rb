class ApplicationController < ActionController::Base
  include Authentication
  # Only allow modern browsers supporting webp images, web push, badges, import maps, CSS nesting, and CSS :has.
  allow_browser versions: :modern

  helper_method :current_user

rescue_from ActiveRecord::RecordNotFound, with: :record_not_found
rescue_from ActiveRecord::RecordInvalid, with: :unprocessable_entity_response
rescue_from ActionController::ParameterMissing, with: :handle_parameter_missing


private
  def record_not_found
    render file: Rails.root.join("public/404.html"), status: :not_found, layout: false
  end

  def unprocessable_entity_response(exception)
    render file: Rails.root.join("public/422.html"), status: :unprocessable_entity
  end

  def handle_parameter_missing
    render file: Rails.root.join("public/400.html"), status: :parameter_missing
  end
  def current_user
    @current_user ||= begin
      session = Session.find_by(id: cookies.signed[:session_token])
      session&.user
    end
  end

  def require_admin
    unless current_user&.admin?
      redirect_to root_path, alert: "You don't have permission to access this page."
    end
  end
end
