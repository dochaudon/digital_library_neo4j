document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('headerSearchToggle');
    const form = document.getElementById('headerSearchForm');
    const input = document.getElementById('headerSearchInput');

    if (toggle && form && input) {
        toggle.addEventListener('click', function(e) {
            if (!form.classList.contains('active')) {
                // Open search
                form.classList.add('active');
                input.focus();
                e.preventDefault();
            } else if (input.value.trim() === '') {
                // Close if empty
                form.classList.remove('active');
                e.preventDefault();
            } else {
                // Submit if has text
                form.classList.remove('active');
                form.submit();
            }
        });

        // Close when clicking outside
        document.addEventListener('click', function(e) {
            if (!form.contains(e.target) && form.classList.contains('active')) {
                form.classList.remove('active');
            }
        });

        // Allow submitting with Enter
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                if (input.value.trim() !== '') {
                    form.classList.remove('active');
                    form.submit();
                } else {
                    e.preventDefault();
                    form.classList.remove('active');
                }
            }
        });
    }
});
