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

### macOS

1. **Install Homebrew**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install Xcode Command Line Tools**

```bash
xcode-select --install
```

3. **Install Required Dependencies**

```bash
brew install openssl@3 libyaml gmp rust readline libffi docker node yarn
```

4. **Install mise (Version Manager)**

```bash
curl https://mise.run | sh
```

Add `mise` to your shell profile:

```bash
echo 'eval "$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc
source ~/.zshrc
```

5. **Set Environment Variables for Ruby Build**

```bash
echo 'export LDFLAGS="-L$(brew --prefix openssl@3)/lib -L$(brew --prefix readline)/lib -L$(brew --prefix libyaml)/lib -L$(brew --prefix gmp)/lib -L$(brew --prefix libffi)/lib"' >> ~/.zshrc
echo 'export CPPFLAGS="-I$(brew --prefix openssl@3)/include -I$(brew --prefix readline)/include -I$(brew --prefix libyaml)/include -I$(brew --prefix gmp)/include -I$(brew --prefix libffi)/include"' >> ~/.zshrc
source ~/.zshrc
```

6. **Install Ruby Using mise**

```bash
mise install ruby@3.2.8
mise use -g ruby@3.2.8
ruby --version
which ruby
```

7. **Install Rails**

```bash
gem install rails
rails --version
```

---

### Linux (Ubuntu or Debian-based)

1. **Install System Dependencies**

```bash
sudo apt-get update
sudo apt install -y build-essential rustc libssl-dev libyaml-dev zlib1g-dev libgmp-dev libffi-dev libreadline-dev git curl nodejs yarn
```

2. **Install mise**

```bash
curl https://mise.run | sh
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc
source ~/.bashrc
```

3. **Install Ruby Using mise**

```bash
mise install ruby@3.2.8
mise use -g ruby@3.2.8
ruby --version
```

4. **Install Rails**

```bash
gem install rails
rails --version
```

---

### Windows (Using WSL)

1. **Install WSL and Ubuntu** Open PowerShell (Admin):

```powershell
wsl --install -d Ubuntu
```

2. **Launch Ubuntu and Update**

```bash
sudo apt-get update && sudo apt-get upgrade
```

3. **Follow the Linux Instructions** Repeat the steps from the Linux section above inside the WSL terminal.

4. **(Optional) Install VS Code Remote - WSL Extension** Use it for easier development inside WSL.

---

## Project Setup

1. **Clone the Repository**

```bash
git clone <repository-url>
cd taco-price-index
```

2. **Install Project Dependencies**

```bash
bundle install
```

3. **Environment Configuration** Create a `.env` file in the project root:

```env
APIKEY=YOURGOOGLEPLACESAPIKEY
POSTGRES_DB=tacos_db
POSTGRES_USER=tacos
POSTGRES_PASSWORD=tacos_password
```

> ⚠️ Never commit the `.env` file to version control.

4. **Database Setup with Docker**

```bash
cd data_collection
docker-compose up -d
cd ..
```

> NOTE: You can also start/stop the PostgreSQL container using `bin/db [up|down]`

Setup the database:

```bash
bin/rails db:migrate
bin/rails db:seed
```

> ⚠️ Do **not** run `bin/rails db:create` — Docker handles database creation.

5. **Start the Development Server**

```bash
bin/rails server
```

Visit `http://localhost:3000`

---

## Development Features

Frontend pages can be accessed at:

- **Map:** `http://localhost:3000/frontend_pages/map`
- **Restaurant Details:** `http://localhost:3000/frontend_pages/restaurant_details`
- **Review Form:** `http://localhost:3000/frontend_pages/restaurant_review_form`
- **User Profile:** `http://localhost:3000/frontend_pages/user_profile`
- **Featured Spotlight:** `http://localhost:3000/frontend_pages/featured_spotlight`
- **Leaderboard:** `http://localhost:3000/frontend_pages/restaurant_leaderboard`
- **Catering/Bulk:** `http://localhost:3000/frontend_pages/catering_bulk_order`

---

## Dummy Email Login

Use the dummy login for frontend testing:

- Email: `test@example.com`
- Password: `password`

---

## Database Configuration

- **Gemfile**: uses `pg`, `dotenv-rails`
- **database.yml**: uses Docker PostgreSQL

---

## Development

### Rails Console

```bash
bin/rails console
```

### Run Tests

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

Python scripts located in `/data_collection`

- `bc_tacos.py`: collect data
- `export_to_rails_seeds.py`: generate seeds

---

## Seeded Data Snapshot

- **153 restaurants**
- **54 taco varieties**
- **540 photos**
- **765 reviews**

Use `bin/rails db:seed` to import.

---

## Contributing

1. Fork
2. Create a feature branch
3. Make changes
4. Run tests
5. Submit PR

---

## Support

If you hit issues, check:

1. This README
2. Docker logs
3. `.env` config
4. Ruby/Rails version

