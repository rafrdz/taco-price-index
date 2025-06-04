# Taco Price Index

A Ruby on Rails application for tracking taco prices across different locations.

---

## Setup Instructions

### Prerequisites

This guide assumes you're using macOS with Apple Silicon (M1/M2/M3). For Intel Macs, paths may differ.

---

### 1. Install Homebrew

If you don't have Homebrew installed:

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
brew install openssl@3 libyaml gmp rust readline libffi
```

---

### 4. Install mise (Version Manager)

```bash
curl https://mise.run | sh
```

Add mise to your shell profile:

```bash
echo 'eval "$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc
source ~/.zshrc
```

---

### 5. Set Environment Variables for Ruby Build

Add these to your `~/.zshrc`:

```bash
echo 'export LDFLAGS="-L$(brew --prefix openssl@3)/lib -L$(brew --prefix readline)/lib -L$(brew --prefix libyaml)/lib -L$(brew --prefix gmp)/lib -L$(brew --prefix libffi)/lib"' >> ~/.zshrc
echo 'export CPPFLAGS="-I$(brew --prefix openssl@3)/include -I$(brew --prefix readline)/include -I$(brew --prefix libyaml)/include -I$(brew --prefix gmp)/include -I$(brew --prefix libffi)/include"' >> ~/.zshrc
source ~/.zshrc
```

---

### 6. Install Ruby using mise

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

You should see Rails 8.0.2 or newer.

---

### 8. Update RubyGems (Optional)

```bash
gem update --system
```

---

## Common Issues

### Ruby Build Fails

Ensure you have the correct environment variables and all dependencies installed. Most errors come from misconfigured OpenSSL or other library paths.

### Version Manager Confusion

If you previously used rbenv or another Ruby version manager, remove it to avoid conflicts:

```bash
brew uninstall rbenv
rm -rf ~/.rbenv
```

Remove any rbenv references from your `~/.zshrc`.

---

## Project Setup

### 1. Clone the Repository

```bash
git clone [repository-url]
cd taco-price-index
```

### 2. Install Project Dependencies

```bash
bundle install
```

### 3. Set Up the Database

```bash
rails db:create
rails db:migrate
rails db:seed # optional
```

### 4. Start the Development Server

```bash
rails server
```

Visit `http://localhost:3000` to see the app.

### 5. Optional: Suppress mise Warnings

```bash
mise settings add idiomatic_version_file_enable_tools ruby
```

---

## Development

### Running Tests

```bash
rails test
```

### Code Quality Tools

The project includes:

- Rubocop: Ruby style enforcement
- Brakeman: Security scanner

Run with:

```bash
bundle exec rubocop
bundle exec brakeman
```

### Background Jobs

The app uses Solid Queue. Start it with:

```bash
bin/jobs
```

---

## Deployment

Deployment is configured with Kamal.

- `config/deploy.yml`: Main configuration
- `.kamal/secrets`: Environment secrets (not committed)

---

## Contributing

Ensure you use the Ruby version specified in this README.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request
