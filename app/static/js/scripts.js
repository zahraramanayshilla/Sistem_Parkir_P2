// scripts.js
document.addEventListener("DOMContentLoaded", function () {

    // --- MENU TOGGLE ---
    const menuToggle = document.getElementById('menu-toggle');
    const navMenu = document.getElementById('nav-menu');
    if (menuToggle) {
        const icon = menuToggle.querySelector('i');
        let isOpen = false;

        menuToggle.addEventListener('click', () => {
            isOpen = !isOpen;
            if (navMenu) navMenu.classList.toggle('hidden');
            if (navMenu) navMenu.classList.toggle('animate-slideDown');

            // Toggle ikon Boxicons
            if (icon) {
                icon.classList.toggle('bx-menu', !isOpen);
                icon.classList.toggle('bx-x', isOpen);
            }
        });
    }

    // --- HASH-BASED VIEW ROUTER ---
    function showView(hash) {
        const views = document.querySelectorAll('[data-view]');
        if (!hash) hash = '#dashboard';

        views.forEach(v => {
            v.classList.toggle('hidden', `#${v.id}` !== hash);
        });

        // Highlight active tab
        document.querySelectorAll('[data-tab]').forEach(tab => {
            tab.classList.remove('bg-blue-600', 'text-white', 'shadow-lg');
            if (tab.getAttribute('href') === hash) {
                tab.classList.add('bg-blue-600', 'text-white', 'shadow-lg');
            }
        });
    }

    window.addEventListener('hashchange', () => showView(location.hash));
    showView(location.hash);

    // --- LOGOUT BUTTON ---
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            // Bisa diganti dengan request ke server logout
            alert("Logout berhasil!");
            window.location.href = "/login";
        });
    }

    // --- OPTIONAL: Add reusable button styles ---
    const btnPrimary = document.querySelectorAll('.btn-primary');
    btnPrimary.forEach(btn => {
        btn.classList.add(
            'inline-flex', 'items-center', 'justify-center', 'gap-2',
            'px-4', 'py-3', 'rounded-xl', 'font-bold', 'text-white',
            'bg-gradient-to-br', 'from-blue-600', 'to-blue-700',
            'shadow-md', 'hover:shadow-lg', 'transition-transform', 'active:translate-y-px'
        );
    });

    const btnSecondary = document.querySelectorAll('.btn-secondary');
    btnSecondary.forEach(btn => {
        btn.classList.add(
            'inline-flex', 'items-center', 'justify-center', 'gap-2',
            'px-4', 'py-3', 'rounded-xl', 'font-bold', 'text-blue-900',
            'bg-white', 'border', 'border-blue-200', 'shadow-md', 'hover:shadow-lg',
            'transition-transform'
        );
    });
});


document.addEventListener("DOMContentLoaded", () => {
    const masukSection = document.getElementById("masuk");
    const cam = document.getElementById("camera-stream");
    const btnBack = document.getElementById("btn-back-dashboard");

    function startCamera() {
        cam.src = "/camera";
    }

    function stopCamera() {
        cam.src = "";
    }

    const observer = new MutationObserver(() => {
        if (!masukSection.classList.contains("hidden")) {
            startCamera();
        } else {
            stopCamera();
        }
    });

    observer.observe(masukSection, { attributes: true });

    btnBack.addEventListener("click", () => {
        stopCamera();
    });
});

