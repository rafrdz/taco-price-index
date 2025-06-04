# Taco Price Index

A Ruby on Rails application for tracking taco prices across different locations.

## Setup Instructions

### Prerequisites

This guide assumes you're using macOS with Apple Silicon (M1/M2/M3). For Intel Macs, paths may differ.

### 1. Install Homebrew

If you don't have Homebrew installed:

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

### 2. Install Xcode Command Line Tools

xcode-select --install

### 3. Install Required Dependencies

brew install openssl@3 libyaml gmp rust readline libffi

### 4. Install mise (Version Manager)

curl https://mise.run | sh

Add mise to your shell profile:

echo 'eval "$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc
source ~/.zshrc

### 5. Set Environment Variables for Ruby Build

Add these to your `~/.zshrc` to ensure Ruby builds correctly on Apple Silicon:

echo 'export LDFLAGS="-L$(brew --prefix openssl@3)/lib -L$(brew --prefix readline)/lib -L$(brew --prefix libyaml)/lib -L$(brew --prefix gmp)/lib -L$(brew --prefix libffi)/lib"' >> ~/.zshrc
echo 'export CPPFLAGS="-I$(brew --prefix openssl@3)/include -I$(brew --prefix readline)/include -I$(brew --prefix libyaml)/include -I$(brew --prefix gmp)/include -I$(brew --prefix libffi)/include"' >> ~/.zshrc
source ~/.zshrc

### 6. Install Ruby using mise

# Install Ruby 3.2.8 (stable version that builds reliably)
mise install ruby@3.2.8

# Set as global version
mise use -g ruby@3.2.8

# Verify installation
ruby --version
which ruby

### 7. Install Rails

gem install rails

# Verify installation
rails --version

You should see Rails 8.0.2 (or newer) installed.

### 8. Update RubyGems (Optional)

gem update --system

## Common Issues

### Ruby Build Fails

If you encounter build errors, ensure you have the environment variables set correctly and all dependencies installed. The most common issue is missing or incorrectly configured paths to OpenSSL and other libraries.

### Version Manager Confusion

If you previously used rbenv or other Ruby version managers, you may want to remove them to avoid conflicts:

# Remove rbenv if previously installed
brew uninstall rbenv
rm -rf ~/.rbenv
# Remove any rbenv references from ~/.zshrc

## Project Setup

Once Ruby and Rails are installed, you can set up the Taco Price Index project:

### 1. Clone the Repository

git clone [repository-url]
cd taco-price-index

### 2. Install Project Dependencies

bundle install

### 3. Set Up the Database

# Create the database
rails db:create

# Run migrations (if any)
rails db:migrate

# Seed the database (optional)
rails db:seed

### 4. Start the Development Server

rails server

Visit `http://localhost:3000` in your browser to see the application running.

### 5. Optional: Suppress mise Warnings

If you see repetitive warnings about idiomatic version files, you can suppress them by enabling the setting:

mise settings add idiomatic_version_file_enable_tools ruby

## Development

### Running Tests

rails test

### Code Quality

The project includes several code quality tools:

- **Rubocop**: Ruby style guide enforcement
- **Brakeman**: Security vulnerability scanner

Run them with:

bundle exec rubocop
bundle exec brakeman

### Background Jobs

The project uses Solid Queue for background job processing. To start the job processor:

bin/jobs

## Deployment

The project is configured for deployment with Kamal. Configuration files are located in:

- `config/deploy.yml` - Main deployment configuration
- `.kamal/secrets` - Environment secrets (not committed to git)

## Contributing

Please ensure you have the correct Ruby version installed as specified in this README before contributing to the project.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and code quality checks
5. Submit a pull request
