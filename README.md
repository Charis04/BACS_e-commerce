# ShopHive

A lightweight e-commerce platform for small businesses to showcase products,
track inventory, and engage with customers via chat.

## Features

* Inventory management
* Real-time chat system
* Secure payment gateway

## Using Codespaces

### Creating a Codespace

1. Navigate to the GitHub repository for ShopHive.
2. Click on the `Code` button.
3. Select the `Codespaces` tab.
4. Click on `New codespace`.

### Running the Application

Once your Codespace is set up:

1. Open a terminal in your Codespace.
2. Ensure all dependencies are installed:

    ```bash
    ./setup.sh
    ```

3. Start the development server:

    ```bash
    flask run
    ```

### Testing the Setup

To ensure the setup is working correctly, run the following commands:

1. Run the test suite:

    ```bash
    pytest
    ```

2. Ensure all tests pass.

## Setting Up Environment Variables

1. Copy `.env.example` to `.env`:

    ```bash
    cp .env.example .env
    ```

## Collaboration

When you've made contributions to the project for the first time, you can run the following to include your name in the `AUTHORS` file:

```bash
.\generate-authors.sh
```
