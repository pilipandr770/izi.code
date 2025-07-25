# 📦 SaaS-магазин на Flask

Повноцінний SaaS-магазин з AI-функціоналом, створений на Flask з багатомовністю та інтеграцією з Stripe.

## 🌟 Особливості

### 🤖 AI-Функціонал
- **AI-консультант**: Чат-бот на основі OpenAI API для допомоги покупцям
- **Автоматична генерація контенту**: AI створює SEO-оптимізовані статті для блогу
- **Персоналізовані рекомендації**: AI аналізує поведінку користувачів

### 🛍️ Електронна комерція
- Управління категоріями та товарами
- Інтеграція з Stripe для безпечних платежів
- Кошик покупок з LocalStorage
- Система замовлень та відстеження

### 🌐 Багатомовність
- Повна підтримка української, російської та німецької мов
- Локалізовані шаблони та контент
- Мовний перемикач для користувачів

### 📱 Адаптивний дизайн
- Responsive Bootstrap 5 інтерфейс
- Мобільна оптимізація
- PWA-готовність

### 🎨 Налаштування
- Динамічні блоки головної сторінки
- Редагування соціальних мереж через адмінку
- Кастомізовані CSS-стилі для різних секцій

## 🔧 Технологічний стек

- **Backend**: Flask 3.0, SQLAlchemy 2.0, PostgreSQL
- **Frontend**: Bootstrap 5, JavaScript ES6+, Jinja2
- **AI**: OpenAI GPT API
- **Платежі**: Stripe Checkout
- **Деплой**: Render.com, Docker-ready

## 📋 Вимоги

- Python 3.11+
- PostgreSQL (для продакшену) або SQLite (для розробки)
- Stripe аккаунт
- OpenAI API ключ

## 🚀 Швидкий старт

### 1. Клонування та налаштування

```bash
git clone <repository-url>
cd saas-shop
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Налаштування змінних середовища

Створіть файл `.env` на основі `.env.example`:

```bash
cp .env.example .env
```

Заповніть необхідні ключі:
- `SECRET_KEY` - секретний ключ Flask
- `STRIPE_PUBLISHABLE_KEY` - публічний ключ Stripe
- `STRIPE_SECRET_KEY` - секретний ключ Stripe
- `OPENAI_API_KEY` - API ключ OpenAI
- `OPENAI_ASSISTANT_ID` - ID асистента OpenAI

### 3. Ініціалізація бази даних

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Запуск локально

```bash
python run.py
```

Додаток буде доступний за адресою: http://localhost:5000

## 🔐 Адміністративна панель

За замовчуванням створюється адмін-користувач:
- **URL**: `/admin`
- **Логін**: admin
- **Пароль**: admin123

Змініть пароль після першого входу!

## 📁 Структура проекту

```
saas-shop/
├── app/                    # Основний код додатку
│   ├── models.py          # SQLAlchemy моделі
│   ├── routes.py          # Flask маршрути
│   ├── forms.py           # WTForms форми
│   ├── utils.py           # Утиліти та AI функції
│   ├── templates/         # Jinja2 шаблони
│   └── static/           # CSS, JS, зображення
├── migrations/            # Alembic міграції
├── config.py             # Конфігурація
├── requirements.txt      # Python залежності
├── run.py               # Точка входу
├── render.yaml          # Конфігурація Render.com
└── README.md            # Документація
```

## 🎯 Основні функції

### Для користувачів:
- Перегляд каталогу товарів по категоріях
- Додавання товарів до кошика
- Безпечна оплата через Stripe
- AI-консультант для допомоги
- Читання блогу з AI-статтями
- Багатомовний інтерфейс

### Для адміністраторів:
- Управління категоріями та товарами
- Створення та редагування блог-постів
- AI-генерація контенту одним кліком
- Налаштування головної сторінки
- Управління соціальними мережами
- Аналітика та статистика

## 🌐 Деплой на Render.com

1. Підключіть репозиторій до Render
2. Використовуйте `render.yaml` для автоматичного налаштування
3. Встановіть змінні середовища в Render Dashboard
4. База даних PostgreSQL створюється автоматично

### Змінні середовища для Render:
```
FLASK_CONFIG=production
SECRET_KEY=<генерується автоматично>
DATABASE_URL=<підключається автоматично>
STRIPE_PUBLISHABLE_KEY=<ваш ключ>
STRIPE_SECRET_KEY=<ваш ключ>
OPENAI_API_KEY=<ваш ключ>
OPENAI_ASSISTANT_ID=<ваш ID>
```

## 🤖 Налаштування AI

### OpenAI Assistant
1. Створіть асистента в OpenAI Playground
2. Навчіть його інформації про ваші товари
3. Вкажіть ID асистента в `OPENAI_ASSISTANT_ID`

### AI-генерація блогу
- Задайте тему в адмін-панелі
- AI створить SEO-оптимізовану статтю
- Автоматичне публікування (опціонально)

## 🔧 Кастомізація

### Додавання нових мов:
1. Додайте мову в `config.py`
2. Створіть переклади в `babel/`
3. Додайте поля в моделях для нової мови

### Налаштування стилів:
- Модифікуйте `static/css/style.css`
- Додайте custom CSS через адмін-панель
- Використовуйте Bootstrap змінні

### Розширення API:
- Додайте нові ендпоінти в `routes.py`
- Створіть нові моделі в `models.py`
- Використовуйте `utils.py` для допоміжних функцій

## 📊 Моніторинг та аналітика

- Логи доступні через Render Dashboard
- Stripe Dashboard для аналітики платежів
- Власна система трекінгу замовлень
- OpenAI Usage для контролю витрат на AI

## 🔒 Безпека

- CSRF захист через Flask-WTF
- Безпечні платежі через Stripe
- Хешування паролів з Werkzeug
- Валідація даних на всіх рівнях
- Rate limiting для API ендпоінтів

## 🧪 Тестування

```bash
# Запуск тестів
python -m pytest tests/

# Покриття коду
python -m pytest --cov=app tests/
```

## 📝 Ліцензія

MIT License - дивіться [LICENSE](LICENSE) файл

## 🤝 Внесення змін

1. Fork репозиторій
2. Створіть feature branch
3. Зробіть commit змін
4. Відправте pull request

## 📞 Підтримка

- **Email**: pylypchukandrii770@gmail.com
- **Telegram**: @borisovi479
- **Issues**: Використовуйте GitHub Issues

## 🔄 Оновлення

Щоб оновити до нової версії:

```bash
git pull origin main
pip install -r requirements.txt
flask db upgrade
```

## 🏆 Автор

**Andrii Pylypchuk**
- Розробник Full-Stack додатків
- Спеціаліст по AI інтеграції
- Flask/Python експерт

---

⭐ Поставте зірочку, якщо проект був корисним!
