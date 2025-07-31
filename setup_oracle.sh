#!/bin/bash

echo "🚀 Настройка Highrise Bot на Oracle Cloud..."

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
echo "🔧 Установка Python и Git..."
sudo apt install python3 python3-pip git screen -y

# Создание директории для бота
echo "📁 Создание директории..."
mkdir -p ~/highrise-bot
cd ~/highrise-bot

# Клонирование проекта (замените на ваш репозиторий)
echo "📥 Загрузка проекта..."
# git clone https://github.com/your-username/your-repo.git .
# Или загрузите файлы вручную

# Установка зависимостей
echo "📚 Установка зависимостей..."
pip3 install highrise-bot-sdk==24.1.0

# Создание systemd сервиса
echo "⚙️ Создание системного сервиса..."
sudo tee /etc/systemd/system/highrise-bot.service > /dev/null <<EOF
[Unit]
Description=Highrise Bot 24/7
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/highrise-bot
ExecStart=/usr/bin/python3 run_forever.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable highrise-bot

echo "✅ Настройка завершена!"
echo "🚀 Для запуска бота выполните:"
echo "   sudo systemctl start highrise-bot"
echo "📊 Для просмотра статуса:"
echo "   sudo systemctl status highrise-bot"
echo "📝 Для просмотра логов:"
echo "   sudo journalctl -u highrise-bot -f" 