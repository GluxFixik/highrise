# 🚀 Простое развертывание на Fly.io

## Почему Fly.io?
✅ **Полностью бесплатно** - 3 VM, 3GB RAM  
✅ **Очень быстро** - глобальная сеть  
✅ **Простая конфигурация** - один файл  
✅ **CLI управление** - удобные команды  

## Быстрые шаги:

### 1. Установка Fly CLI
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Или скачайте с https://fly.io/docs/hands-on/install-flyctl/
```

### 2. Регистрация
```bash
fly auth signup
```

### 3. Развертывание
```bash
# В папке new_bot
fly launch
```

### 4. Запуск
```bash
fly deploy
```

## Управление:
```bash
fly logs          # Логи
fly status        # Статус
fly restart       # Перезапуск
fly destroy       # Удаление
```

## Преимущества:
- Работает 24/7
- Глобальная сеть дата-центров
- Автоматическое масштабирование
- Простое управление через CLI 