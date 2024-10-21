function updateCartItemCount() {
    fetch("{% url 'cart_item_count' %}")
        .then(response => response.json())
        .then(data => {
            document.getElementById('cart-item-count').innerText = data.item_count;
        });
}

document.addEventListener('DOMContentLoaded', function () {
    updateCartItemCount();
});