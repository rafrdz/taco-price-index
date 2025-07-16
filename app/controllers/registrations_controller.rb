class RegistrationsController < ApplicationController
  # Allow users to access the registration form and submit without being authenticated
  allow_unauthenticated_access :new, :create

  def new
    redirect_to root_path if authenticated?
    @user = User.new
  end

  def create
    @user = User.new(registration_params)
    
    if @user.save
      start_new_session_for @user
      redirect_to after_authentication_url, notice: "Welcome! You have signed up successfully."
    else
      render :new, status: :unprocessable_entity
    end
  end

  private

  def registration_params
    params.require(:user).permit(:email_address, :password, :password_confirmation)
  end
end