// KabiyèBooks — Main JS

document.addEventListener('DOMContentLoaded', function () {
    // Auto-close alerts
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Navbar scroll effect
    const navbar = document.getElementById('main-navbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 60) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Quantity input helpers
    document.querySelectorAll('.qty-input').forEach(function (input) {
        const dec = input.parentElement.querySelector('.qty-dec');
        const inc = input.parentElement.querySelector('.qty-inc');
        if (dec) dec.addEventListener('click', function () {
            const v = parseInt(input.value) - 1;
            if (v >= 1) input.value = v;
        });
        if (inc) inc.addEventListener('click', function () {
            const max = parseInt(input.getAttribute('max') || 99);
            const v = parseInt(input.value) + 1;
            if (v <= max) input.value = v;
        });
    });

    // Star rating interactive
    document.querySelectorAll('.star-picker').forEach(function (picker) {
        const stars = picker.querySelectorAll('.star-btn');
        const input = picker.querySelector('input[type=hidden]');
        stars.forEach(function (star, idx) {
            star.addEventListener('mouseover', function () {
                stars.forEach(function (s, i) {
                    s.querySelector('i').className = i <= idx ? 'bi bi-star-fill text-warning' : 'bi bi-star text-muted';
                });
            });
            star.addEventListener('click', function () {
                if (input) input.value = idx + 1;
                stars.forEach(function (s, i) {
                    s.querySelector('i').setAttribute('data-selected', i <= idx);
                });
            });
            picker.addEventListener('mouseleave', function () {
                const selected = input ? parseInt(input.value) : 0;
                stars.forEach(function (s, i) {
                    s.querySelector('i').className = i < selected ? 'bi bi-star-fill text-warning' : 'bi bi-star text-muted';
                });
            });
        });
    });
});

// CSRF helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
