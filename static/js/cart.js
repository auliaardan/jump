function updateCartItemCount() {
    fetch(cartItemCountUrl, {
        credentials: 'same-origin'  // Include credentials in the request
    })
    .then(response => response.json())
    .then(data => {
    });
}
document.addEventListener('DOMContentLoaded', function () {
    updateCartItemCount();
});