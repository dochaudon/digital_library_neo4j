document.addEventListener('DOMContentLoaded', function () {

    /* ═══════════════════════════════════════════════
       HEADER SEARCH (Expanding)
       ═══════════════════════════════════════════════ */
    const toggle = document.getElementById('headerSearchToggle');
    const form = document.getElementById('headerSearchForm');
    const input = document.getElementById('headerSearchInput');

    if (toggle && form && input) {
        toggle.addEventListener('click', function (e) {
            if (!form.classList.contains('active')) {
                form.classList.add('active');
                input.focus();
                e.preventDefault();
            } else if (input.value.trim() === '') {
                form.classList.remove('active');
                e.preventDefault();
            } else {
                form.classList.remove('active');
                form.submit();
            }
        });

        document.addEventListener('click', function (e) {
            if (!form.contains(e.target) && form.classList.contains('active')) {
                form.classList.remove('active');
            }
        });

        input.addEventListener('keypress', function (e) {
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

    /* ═══════════════════════════════════════════════
       MOBILE HAMBURGER MENU & SIDE DRAWER
       ═══════════════════════════════════════════════ */
    const mobileOverlay = document.getElementById('mobileOverlay');

    const hamburgerNavBtn = document.getElementById('hamburgerNavBtn');
    const mobileDrawerNav = document.getElementById('mobileDrawerNav');
    const drawerCloseNav = document.getElementById('drawerCloseNav');

    const hamburgerUserBtn = document.getElementById('hamburgerUserBtn');
    const mobileDrawerAuth = document.getElementById('mobileDrawerAuth');
    const drawerCloseAuth = document.getElementById('drawerCloseAuth');

    function openDrawer(drawer) {
        if (!drawer || !mobileOverlay) return;
        closeAllDrawers(); // Close others first if any
        drawer.classList.add('is-open');
        mobileOverlay.classList.add('is-open');
        document.body.style.overflow = 'hidden';
    }

    function closeAllDrawers() {
        if (mobileDrawerNav) mobileDrawerNav.classList.remove('is-open');
        if (mobileDrawerAuth) mobileDrawerAuth.classList.remove('is-open');
        if (mobileOverlay) mobileOverlay.classList.remove('is-open');
        if (hamburgerNavBtn) hamburgerNavBtn.classList.remove('is-active');
        document.body.style.overflow = '';
    }

    // NAV DRAWER
    if (hamburgerNavBtn) {
        hamburgerNavBtn.addEventListener('click', function () {
            if (mobileDrawerNav && mobileDrawerNav.classList.contains('is-open')) {
                closeAllDrawers();
            } else {
                openDrawer(mobileDrawerNav);
                hamburgerNavBtn.classList.add('is-active');
            }
        });
    }

    if (drawerCloseNav) {
        drawerCloseNav.addEventListener('click', closeAllDrawers);
    }

    // AUTH DRAWER
    if (hamburgerUserBtn) {
        hamburgerUserBtn.addEventListener('click', function () {
            if (mobileDrawerAuth && mobileDrawerAuth.classList.contains('is-open')) {
                closeAllDrawers();
            } else {
                openDrawer(mobileDrawerAuth);
            }
        });
    }

    if (drawerCloseAuth) {
        drawerCloseAuth.addEventListener('click', closeAllDrawers);
    }

    // OVERLAY
    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', closeAllDrawers);
    }

    // ESCAPE KEY
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeAllDrawers();
        }
    });

    // CLOSE ON LINK CLICK
    document.querySelectorAll('.drawer-link, .drawer-user-link, .drawer-auth-btn').forEach(function (link) {
        link.addEventListener('click', closeAllDrawers);
    });

    /* ═══════════════════════════════════════════════
       RESIZE HANDLER
       ═══════════════════════════════════════════════ */
    window.addEventListener('resize', function () {
        if (window.innerWidth > 768) {
            closeAllDrawers();
        }
    });

});
