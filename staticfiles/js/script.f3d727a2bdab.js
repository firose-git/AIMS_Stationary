document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ JavaScript Loaded Successfully");

    // 🛒 Live Search Functionality
    const searchInput = document.getElementById("searchInput");
    const searchResults = document.getElementById("searchResults");
    const clearSearch = document.getElementById("clearSearch");

    const products = [
        "Spiral Notebook", "Notebook", "White Bristol Paper", "Name Stickers", "White Envelopes",
        "Printing Paper", "Document Sleeves", "Plastic Sleeves", "Office Binder", "Plastic Folder",
        "Index", "Folder with Compartments", "Binder", "Cardboard File", "Sharp Pencils",
        "Gel Pen", "Lord Pen", "Thin Lord Pens", "Sharpener", "Highlighter Pen", "Ruler",
        "Glue Stick", "Memory Card", "USB Drive", "Wired Keyboard", "Wired Mouse",
        "Webcam", "Computer Speakers", "External Hard Drive", "Printer Cable", "Scientific Calculator"
    ];

    searchInput.addEventListener("input", function () {
        let query = searchInput.value.toLowerCase();
        searchResults.innerHTML = "";

        if (query.length > 0) {
            clearSearch.style.display = "block";
            let matches = products.filter(product => product.toLowerCase().includes(query));

            if (matches.length > 0) {
                matches.forEach(match => {
                    let item = document.createElement("div");
                    item.classList.add("search-item");
                    item.textContent = match;
                    item.addEventListener("click", function () {
                        searchInput.value = match;
                        searchResults.innerHTML = "";
                    });
                    searchResults.appendChild(item);
                });
            } else {
                searchResults.innerHTML = '<div class="search-item not-found">Product not available</div>';
            }
        } else {
            clearSearch.style.display = "none";
        }
    });

    if (clearSearch) {
        clearSearch.addEventListener("click", function () {
            searchInput.value = "";
            searchResults.innerHTML = "";
            clearSearch.style.display = "none";
        });
    }

    // 🔝 Scroll-to-top button
    let scrollBtn = document.getElementById("scrollTopBtn");
    if (scrollBtn) {
        window.onscroll = function () {
            scrollBtn.style.display = (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) ? "block" : "none";
        };

        scrollBtn.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // 🛒 Add to Cart Functionality
    document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", function () {
            let productId = this.getAttribute("data-product-id");

            if (!productId || productId.trim() === "" || productId === "undefined") {
                console.error("❌ Error: Product ID is missing!");
                alert("Product ID is missing!");
                return;
            }

            console.log("✅ Adding Product ID:", productId);

            fetch("/cart/add/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ product_id: productId })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Server Response:", data);
                alert(data.message);
            })
            .catch(error => console.error("❌ Error adding to cart:", error));
        });
    });

    // Function to Get CSRF Token from Cookie
    function getCSRFToken() {
        let cookieValue = null;
        let cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.startsWith("csrftoken=")) {
                cookieValue = cookie.substring("csrftoken=".length, cookie.length);
                break;
            }
        }
        return cookieValue;
    }
});
