function updateCartIcon() {
        $.ajax({
            url: cartItemCountUrl,
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                var itemCount = data.item_count || 0;
                if (itemCount > 0) {
                    // Add the breathing animation class
                    $('#cart-icon').addClass('breathing');
                } else {
                    // Remove the breathing animation class
                    $('#cart-icon').removeClass('breathing');
                }
            },
            error: function (error) {
                console.error('Error fetching cart item count:', error);
            }
        });
    }

    // Call the function when the page loads
    $(document).ready(function () {
        updateCartIcon();
    });