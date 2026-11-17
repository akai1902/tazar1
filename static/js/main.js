// ===== ТЁМНАЯ/СВЕТЛАЯ ТЕМА =====
function toggleTheme() {
    const body = document.body;
    const icon = document.getElementById('themeIcon');
    
    if (body.classList.contains('dark-mode')) {
        body.classList.remove('dark-mode');
        body.classList.add('light-mode');
        icon.className = 'fas fa-moon';
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
        icon.className = 'fas fa-sun';
        localStorage.setItem('theme', 'dark');
    }
}

// Применяем сохранённую тему
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    document.body.classList.add('dark-mode');
    document.body.classList.remove('light-mode');
    const icon = document.getElementById('themeIcon');
    if (icon) icon.className = 'fas fa-sun';
}

// ===== ПЕРЕКЛЮЧАТЕЛЬ ЯЗЫКА =====
function toggleLang() {
    const dropdown = document.getElementById('langDropdown');
    dropdown.classList.toggle('show');
}

// ===== МОБИЛЬНОЕ МЕНЮ =====
function toggleMobileMenu() {
    const navMenu = document.getElementById('navMenu');
    const toggle = document.querySelector('.mobile-menu-toggle');

    if (!navMenu || !toggle) return;

    navMenu.classList.toggle('mobile-open');
    const isOpen = navMenu.classList.contains('mobile-open');
    toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
}

// Закрыть dropdown если кликнули вне
document.addEventListener('click', function(e) {
    const switcher = document.querySelector('.lang-switcher');
    if (switcher && !switcher.contains(e.target)) {
        document.getElementById('langDropdown').classList.remove('show');
    }

    const navMenu = document.getElementById('navMenu');
    const toggle = document.querySelector('.mobile-menu-toggle');
    if (navMenu && toggle && !navMenu.contains(e.target) && !toggle.contains(e.target)) {
        navMenu.classList.remove('mobile-open');
        toggle.setAttribute('aria-expanded', 'false');
    }
});

const navLinks = document.querySelectorAll('.nav-links a');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        const navMenu = document.getElementById('navMenu');
        const toggle = document.querySelector('.mobile-menu-toggle');
        if (navMenu && toggle) {
            navMenu.classList.remove('mobile-open');
            toggle.setAttribute('aria-expanded', 'false');
        }
    });
});

// ===== СМЕНА ЯЗЫКА ЧЕРЕЗ ПРЕФИКСЫ =====
function changeLanguage(langCode) {
    const currentPath = window.location.pathname;
    // Убираем текущие языковые префиксы /ru/, /ky/, /en/ из начала пути, если они есть
    let cleanPath = currentPath.replace(/^\/(ru|ky|en)(?=\/|$)/, '');
    if (cleanPath === '') cleanPath = '/';

    // Формируем новый путь в зависимости от выбранного языка
    // Поскольку у русского стоит prefix_default_language=False, он идет без префикса
    let newPath = langCode === 'ru' ? cleanPath : '/' + langCode + cleanPath;

    window.location.href = newPath;
}

