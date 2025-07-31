# 🚀 Развертывание бота на бесплатном VPS (24/7)

## Бесплатные VPS провайдеры:

### 1. Oracle Cloud Free Tier
✅ **Навсегда бесплатно** - 2 VM, 24GB RAM  
✅ **Высокая производительность**  
✅ **Надежность**  

### 2. Google Cloud Free Tier
✅ **$300 кредитов** на 12 месяцев  
✅ **После этого** - бесплатный план  
✅ **Простота использования**  

### 3. AWS Free Tier
✅ **12 месяцев бесплатно**  
✅ **После этого** - очень дешево  
✅ **Множество сервисов**  

## Шаги развертывания (Oracle Cloud):

### 1. Регистрация
1. Перейдите на https://www.oracle.com/cloud/free/
2. Зарегистрируйтесь
3. Создайте бесплатный аккаунт

### 2. Создание VM
1. Создайте Ubuntu 22.04 VM
2. Выберите ARM64 (Ampere) - дешевле
3. Настройте SSH ключи

### 3. Подключение и настройка
```bash
# Подключение
ssh ubuntu@your-vm-ip

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python
sudo apt install python3 python3-pip git -y

# Клонирование проекта
git clone your-repo-url
cd new_bot

# Установка зависимостей
pip3 install -r requirements.txt
```

### 4. Запуск с systemd
```bash
# Создание сервиса
sudo nano /etc/systemd/system/highrise-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Highrise Bot 24/7
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/new_bot
ExecStart=/usr/bin/python3 run_forever.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5. Запуск
```bash
sudo systemctl daemon-reload
sudo systemctl enable highrise-bot
sudo systemctl start highrise-bot
sudo systemctl status highrise-bot
```

## Мониторинг:
```bash
# Логи
sudo journalctl -u highrise-bot -f

# Статус
sudo systemctl status highrise-bot

# Перезапуск
sudo systemctl restart highrise-bot
```

## Преимущества VPS:
- Полный контроль
- Неограниченное время работы
- Высокая производительность
- Надежность
- Возможность масштабирования 