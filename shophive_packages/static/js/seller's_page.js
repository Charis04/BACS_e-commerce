// JavaScript for Seller Interface

const apiBaseUrl = "http://127.0.0.1:5003"; // Replace with your API base URL

// Fetch products and display
async function fetchProducts(page = 1, filters = {}) {
    try {
        const response = await fetch(`${apiBaseUrl}/products?page=${page}&category=${filters.category || ''}&tags=${filters.tags || ''}&name=${filters.name || ''}`);
        if (!response.ok) throw new Error(`Error: ${response.status}`);

        const data = await response.json();
        renderProducts(data.products);
        setupPagination(data.totalPages, page);
    } catch (error) {
        console.error("Error fetching products:", error);
        alert("Failed to load products. Check the console for details.");
    }
}

// Render products in the table
function renderProducts(products) {
    const productTable = document.getElementById("product-table");
    productTable.innerHTML = "";

    products.forEach(product => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${product.id}</td>
            <td>${product.name}</td>
            <td>${product.category}</td>
            <td>${product.tags.join(', ')}</td>
        `;
        productTable.appendChild(row);
    });
}

// Setup pagination
function setupPagination(totalPages, currentPage) {
    const pagination = document.getElementById("pagination");
    pagination.innerHTML = "";

    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement("button");
        button.textContent = i;
        button.disabled = i === currentPage;
        button.addEventListener("click", () => fetchProducts(i));
        pagination.appendChild(button);
    }
}

// Add product
document.getElementById("add-product-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
        const response = await fetch(`${apiBaseUrl}/products`, {
            method: "POST",
            body: JSON.stringify(Object.fromEntries(formData)),
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) throw new Error(`Error: ${response.status}`);

        alert("Product added successfully!");
        fetchProducts();
    } catch (error) {
        console.error("Error adding product:", error);
        alert("Failed to add product. Check the console for details.");
    }
});

// Edit product
document.getElementById("edit-product-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const productId = formData.get("id");

    try {
        const response = await fetch(`${apiBaseUrl}/products/${productId}`, {
            method: "PUT",
            body: JSON.stringify(Object.fromEntries(formData)),
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) throw new Error(`Error: ${response.status}`);

        alert("Product updated successfully!");
        fetchProducts();
    } catch (error) {
        console.error("Error updating product:", error);
        alert("Failed to update product. Check the console for details.");
    }
});

// Delete product
document.getElementById("delete-product-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const productId = document.getElementById("delete-product-id").value;

    try {
        const response = await fetch(`${apiBaseUrl}/products/${productId}`, {
            method: "DELETE",
        });

        if (!response.ok) throw new Error(`Error: ${response.status}`);

        alert("Product deleted successfully!");
        fetchProducts();
    } catch (error) {
        console.error("Error deleting product:", error);
        alert("Failed to delete product. Check the console for details.");
    }
});

// Fetch categories and tags for dropdowns
async function fetchDropdownData() {
    try {
        const [categoriesResponse, tagsResponse] = await Promise.all([
            fetch(`${apiBaseUrl}/categories`),
            fetch(`${apiBaseUrl}/tags`),
        ]);

        if (!categoriesResponse.ok || !tagsResponse.ok) throw new Error("Failed to fetch dropdown data.");

        const categories = await categoriesResponse.json();
        const tags = await tagsResponse.json();

        populateDropdown("add-product-category", categories);
        populateDropdown("edit-product-category", categories);
    } catch (error) {
        console.error("Error fetching dropdown data:", error);
    }
}

function populateDropdown(elementId, options) {
    const dropdown = document.getElementById(elementId);
    dropdown.innerHTML = "<option value=''>Select</option>";
    options.forEach(option => {
        const opt = document.createElement("option");
        opt.value = option.id;
        opt.textContent = option.name;
        dropdown.appendChild(opt);
    });
}

// Initialize
fetchProducts();
fetchDropdownData();
