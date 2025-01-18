# ShopHive

![Development Status](https://img.shields.io/badge/status-in%20development-yellow)
![Version](https://img.shields.io/badge/version-0.1.0-blue)

ShopHive is a lightweight e-commerce platform currently in active development. The project aims to provide small businesses with tools to showcase products and manage inventory, with future plans for customer engagement features.

## Current Implementation Status

- ✅ Basic Flask application setup
- ✅ Project structure and organization
- ✅ Initial database models
- ✅ User authentication
- ⏳ Product management (In Progress)
- ✅ Shopping cart functionality
- ⏳ User registration (In Progress)
- 🔜 Payment integration (Planned)
- 🔜 Real-time chat system (Planned)

## Features

### Implemented

- Basic product listing
- Database models for users and products
- Frontend templates structure
- Development environment setup
- User authentication system

### In Progress

- Product management interface
- Basic inventory tracking

### Planned

- Real-time chat system
- Secure payment gateway integration
- Advanced inventory management
- Customer engagement tools

## Project Structure

```bash
shophive_packages/
├── static/                      # Static files for CSS, JS, images
│   └── css/                     # Stylesheets
│       └── style.css
├── templates/                   # Flask Jinja2 templates
│   ├── base.html                # Parent template
│   ├── home.html                # Product listing page
│   ├── add_product.html         # Add product form
│   ├── product_detail.html      # Product details page
├── models/                      # Database models
│   ├── __init__.py
│   ├── cart.py
│   ├── product.py
│   ├── user.py
├── routes/                      # Application routes
│   ├── __init__.py
│   ├── cart_routes.py
│   ├── user_routes.py
│   ├── product_routes.py        # Product-related routes
├── forms/                       # Forms
│   ├── __init__.py
│   ├── product_form.py          # Form for adding/editing products
├── tests/                       # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_homepage.py
│   ├── test_routes.py
│   └── test_models/             # Test models
│       ├── test_product_model.py
│       ├── test_user_model.py
├── app.py                       # Main Flask application
├── config.py                    # Configuration settings
├── setup.sh                     # Script to set up the environment
├── .env.example                 # Example environment variables
├── generate-authors.sh          # Script to generate AUTHORS file
```

---

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment tool (recommended)

### Using Codespaces

1. Navigate to the GitHub repository for ShopHive.
2. Click on the `Code` button.
3. Select the `Codespaces` tab.
4. Click on `New codespace`.

### Local Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Charis04/ShopHive.git
   cd ShopHive
   ```

2. Set up dependencies:

   ```bash
   ./setup.sh
   ```

3. Run the development server:

   ```bash
   flask run
   ```

   OR

   ```bash
   python app.py
   ```

4. Access the app at `http://127.0.0.1:5000`.

---

## Current Development Focus

1. Completing user authentication system
2. Implementing basic product management
3. Setting up testing infrastructure
4. Establishing CI/CD pipeline

## Frontend Development

### Template System

- **Base Template:** Provides a consistent layout with a header, footer, and navigation links.
- **Home Page:** Displays a list of products dynamically.
- **Add Product Page:** Allows users to add new products via a form.
- **Product Detail Page:** Displays detailed information about a specific product.

### Styles and Responsiveness

The frontend uses:

- **CSS:** For custom styling.
- **Bootstrap (optional):** For responsiveness and consistent design.
- **JavaScript (optional):** To add interactivity (e.g., form validation).

### Screenshots (Optional)

- Add screenshots of the home page, add product page, etc.

---

## Testing

Currently implementing test suite. To run available tests:

```bash
pytest -v
```

For coverage reports, you can use:

```bash
pytest --cov=shophive_packages
```

If you want a more detailed coverage report, you can use:

```bash
pytest --cov=shophive_packages --cov-report=term-missing
```

This will show which lines of code are not covered by the tests.

You can also generate an HTML report:

```bash
pytest --cov=shophive_packages --cov-report=html
```

In VS Code terminal, you can open it with:

```bash
# For Linux
python -m http.server --directory htmlcov 8000
```

You can also generate an XML report:

```bash
pytest --cov=shophive_packages --cov-report=xml
```

NOTE: Test coverage is currently being expanded.

---

## Setting Up Environment Variables

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Update the values as needed (e.g., API keys, database URLs).

---

## Contributing

The project is in early development and we welcome contributions! Please check the [Issues](https://github.com/Charis04/ShopHive/issues) tab for current tasks.

We welcome contributions! Follow these steps to get started:

1. Fork the repository and clone it locally.
2. Create a new branch for your feature:

   ```bash
   git checkout -b feature-name
   ```

3. Commit your changes and push to your fork.
4. Open a pull request to the main repository.

### Adding Your Name to AUTHORS

If you're contributing for the first time:

```bash
./generate-authors.sh
```

---

## Roadmap

### Phase 1 (Complete)

- Complete basic authentication
- Implement product CRUD operations
- Set up testing infrastructure

### Phase 2 (Current)

- Shopping cart functionality
- User profiles
- Basic payment integration

### Phase 3 (Future)

- Real-time chat system
- Advanced inventory management
- Analytics dashboard

## Future Improvements

- Enhanced user authentication
- Admin dashboard for managing products
- Integration with external APIs for payments
