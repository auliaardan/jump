$(document).ready(function () {
    let currentPage = 1;
    let searchTimeout;

    function loadSeminars(page, query = '') {
        $.ajax({
            url: "{% url 'seminar_list' %}",
            type: 'GET',
            data: {
                'page': page,
                'search': query,
            },
            success: function (response) {
                const newContent = $(response).find('#seminar-list').html();
                if (newContent.trim() === "" && query === "") {
                    currentPage = 1;
                    loadSeminars(currentPage);
                } else {
                    $('#seminar-list').html(newContent);
                    updateButtons(page);
                }
            },
            error: function (xhr, status, error) {
                console.error('Error:', error);
            }
        });
    }

    function updateButtons(page) {
        $.ajax({
            url: "{% url 'seminar_list' %}",
            type: 'GET',
            data: {
                'page': page,
            },
            success: function (response) {
                const has_next = $(response).find('#next-btn').prop('disabled');
                const has_previous = $(response).find('#prev-btn').prop('disabled');
                $('#next-btn').prop('disabled', has_next);
                $('#prev-btn').prop('disabled', has_previous);
            }
        });
    }

    $('#next-btn').click(function () {
        currentPage++;
        loadSeminars(currentPage);
    });

    $('#prev-btn').click(function () {
        if (currentPage > 1) {
            currentPage--;
            loadSeminars(currentPage);
        }
    });

    $(document).on('click', '.add-to-cart', function () {
        var seminarId = $(this).data('seminar-id');
        var button = $(this);
        const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        $.ajax({
            url: "{% url 'add_to_cart' 0 %}".replace('0', seminarId),
            type: 'POST',
            data: {
                'seminar_id': seminarId,
                'csrfmiddlewaretoken': csrftoken
            },
            xhrFields: {
                withCredentials: true
            },
            success: function (response) {
                if (response.success) {
                    updateCartItemCount();
                    button.text('Added (' + response.quantity + ')');
                    $('p.remaining-seats-' + seminarId).text('Remaining Seats: ' + response.remaining_seats);
                    if (response.remaining_seats <= 0) {
                        button.text('Sold Out');
                        button.prop('disabled', true);
                    }
                    updateCartIcon();
                } else if (response.message === 'not_authenticated') {
                    alert('You need to log in to add items to your cart.');
                } else {
                    alert(response.message);
                    button.text('Sold Out');
                    button.prop('disabled', true);
                }
            },
            error: function (xhr, status, error) {
                console.error('Error:', error);
            }
        });
    });

    $('#seminar-search').on('input', function () {
        clearTimeout(searchTimeout);
        const query = $(this).val().trim();

        if (query) {
            currentPage = 1;
            loadSeminars(currentPage, query);
        } else {
            searchTimeout = setTimeout(function () {
                loadSeminars(currentPage);
            }, 500);
        }
    });
});