document.addEventListener("DOMContentLoaded", function () {
    let buttons = document.querySelectorAll(".add-to-cart");

    buttons.forEach(button => {
        button.addEventListener("click", function () {
            let productId = this.getAttribute("data-id");
            alert(`Product ID: ${productId} added to cart!`);
            // You can extend this to make an AJAX request to add the product to the cart
        });
    });
});
