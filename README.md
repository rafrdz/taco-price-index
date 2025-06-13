# Taco Price Index

A Ruby on Rails application for tracking taco prices across different locations in San Antonio, Texas. This project collects real taco data from the Google Places API and provides a comprehensive database of local taco establishments.

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

```bash
bin/rails generate model Restaurant name:string street_address:string city:string state:string zip:string latitude:decimal longitude:decimal phone:string website:string yelp_id:string

bin/rails generate model Taco restaurant:references name:string description:text price_cents:integer calories:integer tortilla_type:string protein_type:string is_vegan:boolean is_bulk:boolean is_daily_special:boolean available_from:time available_to:time

bin/rails generate model Photo taco:references user_id:uuid url:string is_user_uploaded:boolean

bin/rails generate model Review restaurant:references author_name:string author_url:string google_rating:integer review_text:text review_time:bigint relative_time_description:string language:string review_date:datetime content:text
```

---

## Setup Instructions

### Prerequisites

This guide assumes you're using macOS with Apple Silicon (M1/M2/M3). For Intel Macs, paths may differ.

---

### 1. Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

### 2. Install Xcode Command Line Tools

```bash
xcode-select --install
```

---

### 3. Install Required Dependencies

```bash
brew install openssl@3 libyaml gmp rust readline libffi docker
```

---

### 4. Install mise (Version Manager)

```bash
curl https://mise.run | sh
```

Add `mise` to your shell profile:

```bash
echo 'eval "$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc
source ~/.zshrc
```

---

### 5. Set Environment Variables for Ruby Build

Add to your `~/.zshrc`:

```bash
echo 'export LDFLAGS="-L$(brew --prefix openssl@3)/lib -L$(brew --prefix readline)/lib -L$(brew --prefix libyaml)/lib -L$(brew --prefix gmp)/lib -L$(brew --prefix libffi)/lib"' >> ~/.zshrc
echo 'export CPPFLAGS="-I$(brew --prefix openssl@3)/include -I$(brew --prefix readline)/include -I$(brew --prefix libyaml)/include -I$(brew --prefix gmp)/include -I$(brew --prefix libffi)/include"' >> ~/.zshrc
source ~/.zshrc
```

---

### 6. Install Ruby Using mise

```bash
mise install ruby@3.2.8
mise use -g ruby@3.2.8
ruby --version
which ruby
```

---

### 7. Install Rails

```bash
gem install rails
rails --version
```

You should see Rails `8.0.2` or newer.

---

## Project Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd taco-price-index
```

---

### 2. Install Project Dependencies

```bash
bundle install
```

---

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
APIKEY=YOURGOOGLEPLACESAPIKEY
POSTGRES_DB=tacos_db
POSTGRES_USER=tacos
POSTGRES_PASSWORD=tacos_password
```

> ⚠️ Never commit the `.env` file to version control.

---

### 4. Database Setup with Docker

Start PostgreSQL container:

```bash
cd data_collection
docker-compose up -d
cd ..
```

> NOTE: You can also start/stop the PostgreSQL container using `bin/db [up|down]`

**`data_collection/docker-compose.yml`:**

```yaml
services:
  postgres:
    image: postgres:14-alpine
    container_name: tacos-db
    environment:
      POSTGRES_DB: tacos_db
      POSTGRES_USER: tacos
      POSTGRES_PASSWORD: tacos_password
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U tacos -d tacos_db']
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

Setup the database:

```bash
bin/rails db:migrate
bin/rails db:seed
```

> ⚠️ Do **not** run `bin/rails db:create` — Docker handles database creation.

---

### 5. Start the Development Server

```bash
bin/rails server
```

Visit `http://localhost:3000`

---

## Development Features

To facilitate frontend development, several static HTML pages have been set up. These pages provide basic structures and routes for the frontend team to build upon without immediate backend integration.

To access these pages:

1. Ensure the Rails server is running (`bin/rails server`).
2. Navigate to the following URLs in your browser:
   - **Map:** `http://localhost:3000/frontend_pages/map`
   - **Restaurant Details:** `http://localhost:3000/frontend_pages/restaurant_details`
   - **Restaurant Review Form:** `http://localhost:3000/frontend_pages/restaurant_review_form`
   - **User Profile:** `http://localhost:3000/frontend_pages/user_profile`
   - **Featured Spotlight & Restaurant Deals:** `http://localhost:3000/frontend_pages/featured_spotlight`
   - **Restaurant Leaderboard:** `http://localhost:3000/frontend_pages/restaurant_leaderboard`
   - **Catering and Bulk Order:** `http://localhost:3000/frontend_pages/catering_bulk_order`

## Dummy Email Login

A basic **dummy email login** has been implemented to allow frontend developers to test authenticated user flows.

To use the dummy login:

1.  Visit the login page: `http://localhost:3000/session/new`
2.  Use email: `test@example.com` and password: 'password'. The system is configured to simulate a successful login for frontend display purposes.
3.  This feature is purely for development and will be replaced by a full authentication system in a later iteration.

---

## Database Configuration

### Modified Files

- **Gemfile**

  - Added `pg`
  - Removed `sqlite3`
  - Added `dotenv-rails`

- **config/database.yml**
  - Configured to use Docker PostgreSQL for dev and test
  - Production uses environment variables

---

## Data Exploration

Start the Rails console:

```bash
bin/rails console
# or
bin/rails c
```

Examples:

```ruby
Restaurant.count
Taco.count

restaurant = Restaurant.first
restaurant.tacos

Taco.where.not(price_cents: nil).order(:price_cents).limit(5)
```

Exit with:

```ruby
exit
```

---

## Development

### Running Tests

```bash
bin/rails test
```

### Code Quality

```bash
bin/rubocop
bin/brakeman
```

### Background Jobs

```bash
bin/jobs
```

---

## Data Collection Module

Python scripts are located in `/data_collection`.

- `bc_tacos.py`: Collects taco data
- `export_to_rails_seeds.py`: Exports to Rails seeds
- `docker-compose.yml`: PostgreSQL config

---

## Seeded Data Snapshot

- **153 restaurants**
- **54 taco varieties**
- **540 photos**
- **765 reviews**

> The data collection module is for maintainers. Other devs can use `bin/rails db:seed`.

---

## Fixtures and Test Data

Included in `test/fixtures/`:

- `restaurants.yml`
- `tacos.yml`
- `photos.yml`
- `reviews.yml`

Loaded automatically when running tests.

---

## Troubleshooting

### Ruby Build Issues

Check `openssl`, `readline`, `libyaml`, etc. are installed. Review `LDFLAGS`/`CPPFLAGS`.

### Conflicting Version Managers

If using `rbenv`, remove it:

```bash
brew uninstall rbenv
rm -rf ~/.rbenv
```

Clean up `.zshrc` as needed.

### Docker DB Connection

```bash
docker ps
docker logs tacos-db
```

Ensure `.env` values match Docker.

### Bundle Errors

```bash
bundle clean --force
bundle install
```

---

## Deployment

Configured using [Kamal](https://kamal-docs.vercel.app):

- `config/deploy.yml`
- `.kamal/secrets` (not committed)

---

## Changelog

Recent changes:

- Switched DB from SQLite to PostgreSQL
- Added Docker-based setup
- Implemented Google Places API data scraper
- Seeded database with real taco data
- Built full model relationships

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Make changes
4. Run tests and quality tools:

```bash
bin/rails test && bin/rubocop
```

5. Submit a PR

---

## Development Workflow

```bash
cd data_collection && docker-compose up -d && cd ..
bundle install
bin/rails db:migrate && bin/rails db:seed
bin/rails server
bin/rails test
```

---

## Support

Check:

1. This README
2. Docker container logs
3. `.env` config
4. Ruby/Rails version

> This app was tested on macOS with Apple Silicon.
