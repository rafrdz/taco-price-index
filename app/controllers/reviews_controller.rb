class ReviewsController < ApplicationController
  before_action :require_authentication
  before_action :set_review, only: %i[show edit update destroy]

  def index
    @reviews = Review.all
  end

  def show
  end

  def new
    @review = Review.new
  end

  def edit
  end

  def create
    @review = Review.new(review_params)
    if @review.save
      redirect_to @review, notice: "Review was successfully created."
    else
      render :new, status: :unprocessable_entity
    end
  end

  def update
    if @review.update(review_params)
      redirect_to @review, notice: "Review was successfully updated."
    else
      render :edit, status: :unprocessable_entity
    end
  end

  def destroy
    @review.destroy
    redirect_to reviews_url, notice: "Review was successfully destroyed."
  end

  private
    def set_review
      @review = Review.find(params[:id])
    end

    def review_params
      params.require(:review).permit(:restaurant_id, :author_name, :author_url, :google_rating, :review_text, :review_time, :relative_time_description, :language, :review_date, :content)
    end
end
