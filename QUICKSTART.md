# 🚀 Швидкий старт SaaS-магазину

## Автоматична установка (Windows)

1. **Клонуйте репозиторій**:
   ```bash
   git clone <repository-url>
   cd saas-shop
   ```

2. **Запустіть автоматичне налаштування**:
   ```bash
   setup.bat
   ```
   
   Скрипт автоматично:
   - Створить віртуальне середовище
   - Встановить залежності
   - Створить файл .env
   - Ініціалізує базу даних

3. **Налаштуйте API ключі**:
   Відредагуйте файл `.env` та додайте ваші ключі:
   ```
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   OPENAI_API_KEY=sk-...
   OPENAI_ASSISTANT_ID=asst_...
   ```

4. **Запустіть сервер**:
   ```bash
   start.bat
   ```

## Ручна установка

1. **Створіть віртуальне середовище**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Встановіть залежності**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Налаштуйте змінні середовища**:
   ```bash
   copy .env.example .env
   # Відредагуйте .env файл
   ```

4. **Ініціалізуйте базу даних**:
   ```bash
   flask init-db
   ```

5. **Запустіть сервер**:
   ```bash
   python run.py
   ```

## Доступ до системи

- **Веб-сайт**: http://localhost:5000
- **Адмін-панель**: http://localhost:5000/admin
- **Логін адміна**: admin / admin123

## VS Code команди

Використовуйте `Ctrl+Shift+P` та виберіть:
- `Tasks: Run Task` → `Run Flask Development Server`
- `Tasks: Run Task` → `Install Dependencies`
- `Tasks: Run Task` → `Initialize Database`
- `Tasks: Run Task` → `Run Tests`

## Docker (альтернатива)

```bash
# Локальна розробка
docker-compose up -d

# Або збірка образу
docker build -t saas-shop .
docker run -p 5000:5000 saas-shop
```

## CLI Команди

```bash
# Ініціалізувати БД
flask init-db

# Створити адміна
flask create-admin

# Статистика БД
flask stats

# Скинути БД (обережно!)
flask reset-db

# Тести
python -m pytest tests.py -v
```

## Функціонал

### 🛍️ Магазин
- Каталог товарів з категоріями
- Кошик з LocalStorage
- Інтеграція з Stripe для оплати
- Багатомовний інтерфейс (UK/RU/DE)

### 🤖 AI Функціонал
- Чат-бот консультант на OpenAI
- Автоматична генерація блог-постів
- SEO-оптимізація контенту

### 📱 Адмін-панель
- Управління категоріями/товарами
- Редагування блогу
- AI-генерація контенту
- Налаштування головної сторінки
- Управління соцмережами

### 🎨 Кастомізація
- Динамічні блоки головної сторінки
- CSS класи для різних секцій
- Завантаження зображень
- Редагування соціальних мереж

## Деплой

### Render.com
1. Підключіть GitHub репозиторій
2. Render автоматично використає `render.yaml`
3. Додайте змінні середовища в Dashboard
4. PostgreSQL підключиться автоматично

### Heroku
```bash
# Додайте buildpack для Python
heroku buildpacks:set heroku/python

# Додайте PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Встановіть змінні
heroku config:set FLASK_CONFIG=production
heroku config:set SECRET_KEY=your-secret-key
# ... інші змінні

# Деплой
git push heroku main
```

## Розробка

### Структура файлів
```
app/
├── models.py        # SQLAlchemy моделі
├── routes.py        # Основні маршрути
├── admin_routes.py  # Адмін маршрути
├── forms.py         # WTForms форми
├── utils.py         # AI та утиліти
├── cli.py           # Flask CLI команди
├── templates/       # Jinja2 шаблони
└── static/          # CSS/JS/зображення
```

### Додавання нових функцій
1. Додайте модель в `models.py`
2. Створіть форму в `forms.py`
3. Додайте маршрути в `routes.py`
4. Створіть шаблони в `templates/`
5. Запустіть міграцію: `flask db migrate`

## Підтримка

- **Email**: pylypchukandrii770@gmail.com
- **Telegram**: @borisovi479
- **GitHub Issues**: для багів та пропозицій

## Ліцензія

MIT License - вільне використання та модифікація

---

💡 **Порада**: Після першого запуску змініть адмін-пароль через панель адміністратора!
