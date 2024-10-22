function updateCartItemCount() {
    fetch(cartItemCountUrl, {
        credentials: 'same-origin'  // Include credentials in the request
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('cart-item-count').innerText = data.item_count;
    });
}
document.addEventListener('DOMContentLoaded', function () {
    updateCartItemCount();
});