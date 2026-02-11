// ========================
// Модальное окно удаления профиля
// ========================

let isDeleting = false;

function showDeleteConfirmation() {
    console.log('Открываем модальное окно');
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeDeleteModal() {
    console.log('Закрываем модальное окно');
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function executeDeleteProfile() {
    console.log('Выполняем удаление профиля');
    if (isDeleting) return;
    
    isDeleting = true;
    
    const btn = document.querySelector('.modal-buttons .btn-danger');
    if (!btn) {
        isDeleting = false;
        return;
    }
    
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span style="display:inline-block;width:20px;height:20px;border:3px solid #fff;border-top-color:transparent;border-radius:50%;animation:spin 1s linear infinite;"></span> Удаление...';
    btn.disabled = true;

    fetch('/delete-profile/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            window.location.href = '/';
        } else {
            alert(data.error || 'Ошибка при удалении профиля');
            btn.innerHTML = originalText;
            btn.disabled = false;
            isDeleting = false;
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при удалении профиля. Попробуйте ещё раз.');
        btn.innerHTML = originalText;
        btn.disabled = false;
        isDeleting = false;
    });
}

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

// Закрытие модального окна при клике вне его
document.addEventListener('click', function(event) {
    const modal = document.getElementById('deleteModal');
    if (modal && modal.style.display === 'block' && event.target === modal) {
        closeDeleteModal();
    }
});

// ========================
// Анимация появления контента
// ========================

document.addEventListener('DOMContentLoaded', function () {
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

// ========================
// FAQ аккордеон
// ========================

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

// ========================
// Переключатель видимости пароля
// ========================

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
                    this.src = showSrc + '?t=' + Date.now(); // ← ДОБАВЛЕНО
                    this.setAttribute('data-state', 'visible');
                    this.alt = "Скрыть пароль";
                } else {
                    input.type = 'password';
                    this.src = hideSrc + '?t=' + Date.now(); // ← ДОБАВЛЕНО
                    this.setAttribute('data-state', 'hidden');
                    this.alt = "Показать пароль";
                }
            });
        });
    }
});

// ========================
// Фильтры и сортировка проектов
// ========================

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

// ========================
// Обновление интерфейса авторизации
// ========================

document.addEventListener('DOMContentLoaded', function () {
    updateAuthUI();
});

function updateAuthUI() {
    const authContainer = document.getElementById('auth-buttons');
    if (!authContainer) return;

    const user = window.user_data;
    const token = localStorage.getItem('token');

    if (token || user) {
        const nickname = user?.username || 'Пользователь';
        
        let avatarUrl = '/static/Image/default-avatar.png';
        
        if (user?.avatar && user.avatar.trim() !== '') {
            if (user.avatar.startsWith('/media/')) {
                avatarUrl = user.avatar;
            } 
            else if (user.avatar.startsWith('/static/')) {
                avatarUrl = user.avatar;
            }
            else {
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
        authContainer.innerHTML = `
            <a href="/enter/" class="auth-link" style="text-decoration: none; color: #000; font-weight: 500;">
                Вход/Регистрация
            </a>
        `;
    }
}

// ========================
// Кнопка "Создать проект"
// ========================

document.addEventListener('DOMContentLoaded', function () {
    const createProjectLink = document.getElementById('create-project-link');
    if (createProjectLink) {
        createProjectLink.addEventListener('click', function (e) {
            e.preventDefault();
            
            const token = localStorage.getItem('token');
            if (token) {
                window.location.href = '/create-project/';
            } else {
                window.location.href = '/register/';
            }
        });
    }
});