document.addEventListener('DOMContentLoaded', function () {
    // Создаём Observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Опционально: отключить после первого срабатывания
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15  // Запускать, когда 15% элемента видно
    });

    // Наблюдаем за .welcome-content
    const welcomeContent = document.querySelector('.welcome-content');
    if (welcomeContent) {
        observer.observe(welcomeContent);
    }
});
document.querySelectorAll('.faq-btn').forEach(button => {
    button.addEventListener('click', () => {
        const answer = button.nextElementSibling;
        const isExpanded = button.getAttribute('aria-expanded') === 'true';

        // Закрываем все ответы
        document.querySelectorAll('.faq-answer').forEach(el => {
            el.classList.remove('show');
            el.previousElementSibling.setAttribute('aria-expanded', 'false');
        });

        // Открываем текущий (если был закрыт)
        if (!isExpanded) {
            answer.classList.add('show');
            button.setAttribute('aria-expanded', 'true');
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const toggles = document.querySelectorAll('.toggle-password');
    
    toggles.forEach(img => {
        img.addEventListener('click', function() {
            const inputId = this.getAttribute('data-target');
            const input = document.getElementById(inputId);
            const currentState = this.getAttribute('data-state');
            const showSrc = this.dataset.showSrc;  // ← из data-show-src
            const hideSrc = this.dataset.hideSrc;  // ← из data-hide-src
            
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
});

document.addEventListener('DOMContentLoaded', function() {
    const chips = document.querySelectorAll('.chip[data-filter]');
    const cards = document.querySelectorAll('.project-card');
    const dropdown = document.getElementById('sortDropdown');
    const toggleBtn = dropdown.querySelector('.dropdown-toggle');
    const menuItems = dropdown.querySelectorAll('.dropdown-menu button');

    // === Фильтрация по категории/статусу ===
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const group = chip.closest('.filter-chips');
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

    // === Сортировка через кастомный dropdown ===
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            const value = item.dataset.value;
            const label = item.textContent;
            
            // Обновляем текст кнопки
            toggleBtn.innerHTML = label + ' <span class="dropdown-arrow">▼</span>';
            
            // Закрываем меню
            dropdown.classList.remove('active');
            
            // Логика сортировки (в реальном проекте — AJAX или перезагрузка)
            console.log('Сортировка по:', value);
            
            // Пример: можно вызвать фильтр + сортировку
            applyFiltersAndSort(value);
        });
    });

    // Вспомогательная функция (заглушка)
    function applyFiltersAndSort(sortBy) {
        // Здесь позже: отправка формы / fetch / пересортировка DOM
        // Пока просто лог:
        console.log('Применена сортировка:', sortBy);
    }

    // Закрытие по клику вне dropdown (опционально, но удобно)
    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('active');
        }
    });

    toggleBtn.addEventListener('click', () => {
        dropdown.classList.toggle('active');
    });
});

