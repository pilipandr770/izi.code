-- Скрипт для добавления недостающих столбцов
ALTER TABLE \
AndriIT\.blog_posts ADD COLUMN IF NOT EXISTS title VARCHAR(200) NOT NULL DEFAULT '';
ALTER TABLE \AndriIT\.blog_posts ADD COLUMN IF NOT EXISTS content TEXT NOT NULL DEFAULT '';
ALTER TABLE \AndriIT\.blog_posts ADD COLUMN IF NOT EXISTS excerpt TEXT;
