# Taco Price Index

A Ruby on Rails application for tracking taco prices across different locations in San Antonio, Texas. This project collects real taco data from Google Places API and provides a comprehensive database of local taco establishments.

---

## Project Overview

The Taco Price Index consists of:
- **Rails API**: Core application with PostgreSQL database
- **Data Collection Module**: Python scripts for scraping Google Places API
- **Seeded Database**: Pre-populated with real San Antonio taco data

### Database Models

The application uses four main models with the following relationships:

- **Restaurant**: Taco establishments with location data
- **Taco**: Individual taco items with pricing and details
- **Photo**: Images associated with tacos
- **Review**: Google Places reviews for restaurants

**Model Generation Commands Used:**

rails generate model Restaurant name:string street_address:string city:string state:string zip:string latitude:decimal longitude:decimal phone:string website:string yelp_id:string

rails generate model Taco restaurant:references name:string description:text price_cents:integer calories:integer tortilla_type:string protein_type:string is_vegan:boolean is_bulk:boolean is_daily_special:boolean available_from:time available_to:time

rails generate model Photo taco:references user_id:uuid url:string is_user_uploaded:boolean

rails generate model Review restaurant:references author_name:string author_url:string google_rating:integer review_text:text review_time:bigint relative_time_description:string language:string review_date:datetime content:text

---

## Setup Instructions

### Prerequisites

This guide assumes you're using macOS with Apple Silicon (M1/M2/M3). For Intel Macs, paths may differ.

---

### 1. Install Homebrew

If you don't have Homebrew installed:

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

---

### 2. Install Xcode Command Line Tools

xcode-select --install

---

### 3. Install Required Dependencies

brew install openssl@3 libyaml gmp rust readline libffi docker

---

### 4. Install mise (Version Manager)

curl https://mise.run | sh

Add mise to your shell profile:

echo 'eval "$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc
source ~/.zshrc

---

### 5. Set Environment Variables for Ruby Build

Add these to your ~/.zshrc:

echo 'export LDFLAGS="-L$(brew --prefix openssl@3)/lib -L$(brew --prefix readline)/lib -L$(brew --prefix libyaml)/lib -L$(brew --prefix gmp)/lib -L$(brew --prefix libffi)/lib"' >> ~/.zshrc
echo 'export CPPFLAGS="-I$(brew --prefix openssl@3)/include -I$(brew --prefix readline)/include -I$(brew --prefix libyaml)/include -I$(brew --prefix gmp)/include -I$(brew --prefix libffi)/include"' >> ~/.zshrc
source ~/.zshrc

---

### 6. Install Ruby using mise

mise install ruby@3.2.8
mise use -g ruby@3.2.8
ruby --version
which ruby

---

### 7. Install Rails

gem install rails
rails --version

You should see Rails 8.0.2 or newer.

---

## Project Setup

### 1. Clone the Repository

git clone [repository-url]
cd taco-price-index

### 2. Install Project Dependencies

**Always run this after cloning or when Gemfile changes:**

bundle install

**When to use bundle install:**
- After cloning the repository
- When someone adds/updates gems in the Gemfile
- When you see bundler-related errors
- After switching branches that may have different dependencies

---

### 3. Environment Configuration

Create a .env file in the project root:

.env file contents:
APIKEY=YOURGOOGLEPLACESAPIKEY
POSTGRES_DB=tacos_db
POSTGRES_USER=tacos
POSTGRES_PASSWORD=tacos_password

**Important Notes:**
- Replace YOURGOOGLEPLACESAPIKEY with your actual Google Places API key
- The database credentials must match the Docker configuration
- Never commit the .env file to version control

---

### 4. Database Setup with Docker

**Start PostgreSQL Container:**

cd data_collection
docker-compose up -d
cd ..

**Docker Configuration** (data_collection/docker-compose.yml):

services:
postgres:
image: postgres:14-alpine
container_name: tacos-db
environment:
POSTGRES_DB: tacos_db
POSTGRES_USER: tacos
POSTGRES_PASSWORD: tacos_password
ports:
- "5432:5432"
volumes:
- postgres_data:/var/lib/postgresql/data
restart: unless-stopped
healthcheck:
test: ["CMD-SHELL", "pg_isready -U tacos -d tacos_db"]
interval: 10s
timeout: 5s
retries: 5

volumes:
postgres_data:

**Setup Database Tables and Data:**

rails db:migrate
rails db:seed

**Important:** Do NOT run rails db:create - the Docker container handles database creation automatically.

---

### 5. Start the Development Server

rails server

Visit http://localhost:3000 to see the app.

---

## Database Configuration

### Modified Files

**Gemfile Changes:**
- Added pg gem for PostgreSQL support
- Removed sqlite3 dependency
- Added dotenv-rails for environment variable management

**database.yml Configuration:**
The application is configured to use PostgreSQL instead of SQLite:
- Development and test databases connect to the Docker PostgreSQL container
- Production uses environment variables for database connection

---

## Data Exploration

### Rails Console

Use Rails console to interact with your data:

rails console
or
rails c

**Rails Console** provides an interactive Ruby environment where you can:
- Query your database using ActiveRecord models
- Test relationships between models
- Debug data issues
- Experiment with Ruby code

**Example console commands:**

Check data counts
Restaurant.count
Taco.count

Explore relationships
restaurant = Restaurant.first
restaurant.tacos

Find cheapest tacos
Taco.where.not(price_cents: nil).order(:price_cents).limit(5)

Exit console
exit

---

## Development

### Running Tests

rails test

### Code Quality Tools

The project includes:

- Rubocop: Ruby style enforcement
- Brakeman: Security scanner

Run with:

bundle exec rubocop
bundle exec brakeman

### Background Jobs

The app uses Solid Queue. Start it with:

bin/jobs

---

## Data Collection Module

### Overview

The /data_collection directory contains Python scripts for gathering real taco data from Google Places API.

**Key Components:**
- bc_tacos.py: Main data collection script
- export_to_rails_seeds.py: Exports PostgreSQL data to Rails-compatible seed files
- docker-compose.yml: PostgreSQL container configuration

### Current Data

The seeded database includes:
- **153 restaurants** in San Antonio area
- **54 unique taco varieties**
- **540 photos** from Google Places
- **765 customer reviews**

**Note:** The data collection module is primarily for project maintainers. Regular developers can use the pre-seeded data via rails db:seed.

---

## Fixtures and Test Data

The application includes comprehensive test fixtures for all models:
- restaurants.yml: Sample restaurant data for testing
- tacos.yml: Various taco types and pricing scenarios
- photos.yml: Test photo associations
- reviews.yml: Sample review data

Fixtures are automatically loaded during test runs and provide consistent test data.

---

## Common Issues

### Ruby Build Fails

Ensure you have the correct environment variables and all dependencies installed. Most errors come from misconfigured OpenSSL or other library paths.

### Version Manager Confusion

If you previously used rbenv or another Ruby version manager, remove it to avoid conflicts:

brew uninstall rbenv
rm -rf ~/.rbenv

Remove any rbenv references from your ~/.zshrc.

### Database Connection Issues

- Ensure Docker container is running: docker ps
- Check container logs: docker logs tacos-db
- Verify environment variables match Docker configuration

### Bundle Install Issues

If you encounter gem installation errors:

Clean bundle cache
bundle clean --force

Reinstall gems
bundle install

---

## Deployment

Deployment is configured with Kamal.

- config/deploy.yml: Main configuration
- .kamal/secrets: Environment secrets (not committed)

---

## Changelog

### Recent Updates

- **Database Migration**: Converted from SQLite to PostgreSQL
- **Docker Integration**: Added containerized PostgreSQL setup
- **Data Collection**: Implemented Google Places API scraping
- **Seeded Data**: Pre-populated database with real San Antonio taco data
- **Model Relationships**: Established comprehensive associations between restaurants, tacos, photos, and reviews

---

## Contributing

Ensure you use the Ruby version specified in this README.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks: rails test && bundle exec rubocop
5. Submit a pull request

### Development Workflow

1. Start Docker container: cd data_collection && docker-compose up -d && cd ..
2. Install dependencies: bundle install
3. Set up database: rails db:migrate && rails db:seed
4. Start server: rails server
5. Make changes and test: rails test

---

## Support

For issues related to setup or development, please check:
1. This README for common solutions
2. Docker container status and logs
3. Environment variable configuration
4. Ruby and Rails versions

The application has been tested on macOS with Apple Silicon and should work on similar Unix-like systems with appropriate adjustments.