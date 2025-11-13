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