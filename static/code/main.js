document.addEventListener('DOMContentLoaded', function () {
    // Создаём Observer для анимации появления
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15
    });

    const welcomeContent = document.querySelector('.welcome-content');
    if (welcomeContent) {
        observer.observe(welcomeContent);
    }
});

// FAQ аккордеон
document.addEventListener('DOMContentLoaded', function() {
    const faqButtons = document.querySelectorAll('.faq-btn');
    if (faqButtons.length > 0) {
        faqButtons.forEach(button => {
            button.addEventListener('click', () => {
                const answer = button.nextElementSibling;
                const isExpanded = button.getAttribute('aria-expanded') === 'true';

                document.querySelectorAll('.faq-answer').forEach(el => {
                    el.classList.remove('show');
                    el.previousElementSibling.setAttribute('aria-expanded', 'false');
                });

                if (!isExpanded) {
                    answer.classList.add('show');
                    button.setAttribute('aria-expanded', 'true');
                }
            });
        });
    }
});

// Переключатель видимости пароля
document.addEventListener('DOMContentLoaded', function() {
    const toggles = document.querySelectorAll('.toggle-password');
    if (toggles.length > 0) {
        toggles.forEach(img => {
            img.addEventListener('click', function() {
                const inputId = this.getAttribute('data-target');
                const input = document.getElementById(inputId);
                if (!input) return;
                
                const currentState = this.getAttribute('data-state');
                const showSrc = this.dataset.showSrc;
                const hideSrc = this.dataset.hideSrc;
                
                if (currentState === 'hidden') {
                    input.type = 'text';
                    this.src = showSrc;
                    this.setAttribute('data-state', 'visible');
                    this.alt = "Скрыть пароль";
                } else {
                    input.type = 'password';
                    this.src = hideSrc;
                    this.setAttribute('data-state', 'hidden');
                    this.alt = "Показать пароль";
                }
            });
        });
    }
});

// Фильтры и сортировка проектов
document.addEventListener('DOMContentLoaded', function() {
    const chips = document.querySelectorAll('.chip[data-filter]');
    const cards = document.querySelectorAll('.project-card');
    const dropdown = document.getElementById('sortDropdown');
    
    // Фильтрация по категории/статусу
    if (chips.length > 0 && cards.length > 0) {
        chips.forEach(chip => {
            chip.addEventListener('click', () => {
                const group = chip.closest('.filter-chips');
                if (!group) return;
                
                group.querySelectorAll('.chip').forEach(c => c.classList.remove('chip-active'));
                chip.classList.add('chip-active');

                const catFilter = document.querySelector('.filter-group:nth-of-type(1) .chip-active')?.dataset.filter || 'all';
                const statFilter = document.querySelector('.filter-group:nth-of-type(2) .chip-active')?.dataset.filter || 'status-all';

                cards.forEach(card => {
                    const cat = card.dataset.category;
                    const stat = card.dataset.status;
                    const show = (catFilter === 'all' || catFilter === cat) &&
                                 (statFilter === 'status-all' || statFilter === `status-${stat}`);
                    card.style.display = show ? 'flex' : 'none';
                });
            });
        });
    }

    // Сортировка через кастомный dropdown
    if (dropdown) {
        const menuItems = dropdown.querySelectorAll('.dropdown-menu button');
        const toggleBtn = dropdown.querySelector('.dropdown-toggle');
        
        if (toggleBtn && menuItems.length > 0) {
            menuItems.forEach(item => {
                item.addEventListener('click', () => {
                    const value = item.dataset.value;
                    const label = item.textContent;
                    
                    toggleBtn.innerHTML = label + ' <span class="dropdown-arrow">▼</span>';
                    dropdown.classList.remove('active');
                    
                    console.log('Сортировка по:', value);
                    applyFiltersAndSort(value);
                });
            });

            toggleBtn.addEventListener('click', () => {
                dropdown.classList.toggle('active');
            });

            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target)) {
                    dropdown.classList.remove('active');
                }
            });
        }
    }

    function applyFiltersAndSort(sortBy) {
        console.log('Применена сортировка:', sortBy);
    }
});

// 🔥 КРИТИЧЕСКИ ВАЖНО: Обновление интерфейса авторизации
document.addEventListener('DOMContentLoaded', function () {
    updateAuthUI();
});

function updateAuthUI() {
    const authContainer = document.getElementById('auth-buttons');
    if (!authContainer) return;

    // Получаем данные из глобальной переменной
    const user = window.user_data;
    const token = localStorage.getItem('token');

    if (token || user) {
        // 🔸 Авторизован - показываем аватар и логин
        const nickname = user?.username || 'Пользователь';
        
        // 🔥 Обработка пути к аватару
        let avatarUrl = '/static/Image/default-avatar.png';
        if (user?.avatar) {
            // Если аватар начинается с /media/ - используем как есть
            // Если начинается с /static/ - используем как есть
            // Иначе добавляем /media/
            if (user.avatar.startsWith('/media/') || user.avatar.startsWith('/static/')) {
                avatarUrl = user.avatar;
            } else {
                avatarUrl = '/media/' + user.avatar;
            }
        }

        authContainer.innerHTML = `
            <a href="/profile/" class="auth-avatar-link" style="display: flex; align-items: center; gap: 8px; text-decoration: none; color: #000;">
                <img src="${avatarUrl}" 
                     alt="Аватар" 
                     class="auth-avatar"
                     style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 2px solid #000;">
                <span class="auth-nickname" style="font-size: 16px; font-weight: 500;">
                    ${nickname}
                </span>
            </a>
        `;
    } else {
        // 🔸 Не авторизован - показываем кнопку входа
        authContainer.innerHTML = `
            <a href="/enter/" class="auth-link" style="text-decoration: none; color: #000; font-weight: 500;">
                Вход/Регистрация
            </a>
        `;
    }
}

// Кнопка "Создать проект"
document.addEventListener('DOMContentLoaded', function () {
    const createProjectLink = document.getElementById('create-project-link');
    if (createProjectLink) {
        createProjectLink.addEventListener('click', function (e) {
            e.preventDefault();
            
            const token = localStorage.getItem('token');
            if (token) {
                // Авторизован — идём на создание проекта
                window.location.href = '/create-project/';
            } else {
                // Не авторизован — идём на регистрацию
                window.location.href = '/register/';
            }
        });
    }
});