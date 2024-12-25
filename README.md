# ShopHive

ShopHive is a lightweight e-commerce platform designed for small businesses to showcase products, manage inventory, and engage with customers in real time. It is built using Flask with a focus on simplicity, scalability, and seamless integration of both frontend and backend functionalities.

## Features

- Inventory management
- Real-time chat system
- Secure payment gateway
- Responsive user interface with HTML, CSS, and Flask templates
- Easy navigation and dynamic product pages

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
├── forms/                       # Forms
│   ├── __init__.py
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
```

---

## Setting Up the Development Environment

### Using Codespaces

1. Navigate to the GitHub repository for ShopHive.
2. Click on the `Code` button.
3. Select the `Codespaces` tab.
4. Click on `New codespace`.

### Local Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Charis04/ShopHive.git
   cd shophive
   ```

2. Set up dependencies:

   ```bash
   ./setup.sh
   ```

3. Run the development server:

   ```bash
   flask run
   ```

4. Access the app at `http://127.0.0.1:5000`.

---

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

## Testing the Application

To ensure the setup works correctly:

1. Run the test suite:

   ```bash
   pytest
   ```

2. Confirm all tests pass.

---

## Setting Up Environment Variables

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Update the values as needed (e.g., API keys, database URLs).

---

## Contribution Guide

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

## Future Improvements

- Enhanced user authentication
- Admin dashboard for managing products
- Integration with external APIs for payments
