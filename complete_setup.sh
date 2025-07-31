#!/bin/bash

echo "🚀 Полная настройка Highrise Bot на Oracle Cloud"
echo "=================================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция логирования
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ОШИБКА]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[ПРЕДУПРЕЖДЕНИЕ]${NC} $1"
}

# Проверка прав администратора
if [ "$EUID" -eq 0 ]; then
    error "Не запускайте скрипт от root пользователя!"
    exit 1
fi

log "Начинаем настройку..."

# Обновление системы
log "📦 Обновление системы..."
sudo apt update
if [ $? -ne 0 ]; then
    error "Ошибка при обновлении системы"
    exit 1
fi

sudo apt upgrade -y
if [ $? -ne 0 ]; then
    error "Ошибка при обновлении пакетов"
    exit 1
fi

# Установка необходимых пакетов
log "🔧 Установка Python и необходимых пакетов..."
sudo apt install python3 python3-pip python3-venv git curl wget screen htop -y
if [ $? -ne 0 ]; then
    error "Ошибка при установке пакетов"
    exit 1
fi

# Создание директории для бота
log "📁 Создание рабочей директории..."
mkdir -p ~/highrise-bot
cd ~/highrise-bot

# Создание виртуального окружения
log "🐍 Создание виртуального окружения Python..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
log "📚 Установка зависимостей..."
pip install --upgrade pip
pip install highrise-bot-sdk==24.1.0
if [ $? -ne 0 ]; then
    error "Ошибка при установке зависимостей"
    exit 1
fi

# Создание systemd сервиса
log "⚙️ Создание системного сервиса..."
sudo tee /etc/systemd/system/highrise-bot.service > /dev/null <<EOF
[Unit]
Description=Highrise Bot 24/7
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/highrise-bot
Environment=PATH=/home/ubuntu/highrise-bot/venv/bin
ExecStart=/home/ubuntu/highrise-bot/venv/bin/python run_forever.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=highrise-bot

# Ограничения ресурсов
LimitNOFILE=65536
LimitNPROC=4096

# Перезапуск при различных ошибках
RestartPreventExitStatus=0 SIGTERM
TimeoutStartSec=60
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd
log "🔄 Перезагрузка systemd..."
sudo systemctl daemon-reload

# Включение автозапуска
log "✅ Включение автозапуска..."
sudo systemctl enable highrise-bot

# Создание скрипта управления
log "🛠️ Создание скрипта управления..."
cat > ~/highrise-bot/manage_bot.sh <<'EOF'
#!/bin/bash

case "$1" in
    start)
        echo "🚀 Запуск бота..."
        sudo systemctl start highrise-bot
        ;;
    stop)
        echo "🛑 Остановка бота..."
        sudo systemctl stop highrise-bot
        ;;
    restart)
        echo "🔄 Перезапуск бота..."
        sudo systemctl restart highrise-bot
        ;;
    status)
        echo "📊 Статус бота:"
        sudo systemctl status highrise-bot
        ;;
    logs)
        echo "📝 Логи бота (Ctrl+C для выхода):"
        sudo journalctl -u highrise-bot -f
        ;;
    logs-recent)
        echo "📝 Последние логи:"
        sudo journalctl -u highrise-bot --no-pager -n 50
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status|logs|logs-recent}"
        exit 1
        ;;
esac
EOF

chmod +x ~/highrise-bot/manage_bot.sh

# Создание файла конфигурации по умолчанию
log "⚙️ Создание конфигурации по умолчанию..."
if [ ! -f ~/highrise-bot/config.json ]; then
    cat > ~/highrise-bot/config.json <<'EOF'
{
  "bot_token": "YOUR_BOT_TOKEN_HERE",
  "room_id": "YOUR_ROOM_ID_HERE",
  "admin_ids": ["YOUR_ADMIN_ID_HERE"],
  "owner_id": "YOUR_OWNER_ID_HERE",
  "moderator_ids": ["YOUR_MODERATOR_ID_HERE"],
  "vip_zone": {
    "x": 13.0,
    "y": 20.0,
    "z": 5.0
  },
  "forbidden_zones": [],
  "bot_wallet": 0,
  "duel_arena": {
    "x": 16,
    "y": 15,
    "z": 16
  },
  "vip_price_monthly": 400,
  "marriage_divorce_cost": 50,
  "free_divorce_days": 14,
  "warning_expire_days": 1,
  "announcements": [
    "Привет! Мы ищем новых ботов. Если ты готов/а к большой и длительной работе, то напиши владельцам об этом!"
  ],
  "announcement_interval": 600
}
EOF
    warning "Создан файл config.json с шаблоном. Отредактируйте его перед запуском!"
fi

# Создание директории для данных
log "📁 Создание директории для данных..."
mkdir -p ~/highrise-bot/data

# Настройка прав доступа
log "🔐 Настройка прав доступа..."
sudo chown -R ubuntu:ubuntu ~/highrise-bot
chmod -R 755 ~/highrise-bot

# Создание алиасов для удобства
log "🔧 Создание алиасов..."
echo "alias bot-start='~/highrise-bot/manage_bot.sh start'" >> ~/.bashrc
echo "alias bot-stop='~/highrise-bot/manage_bot.sh stop'" >> ~/.bashrc
echo "alias bot-restart='~/highrise-bot/manage_bot.sh restart'" >> ~/.bashrc
echo "alias bot-status='~/highrise-bot/manage_bot.sh status'" >> ~/.bashrc
echo "alias bot-logs='~/highrise-bot/manage_bot.sh logs'" >> ~/.bashrc
echo "alias bot-logs-recent='~/highrise-bot/manage_bot.sh logs-recent'" >> ~/.bashrc
echo "alias cd-bot='cd ~/highrise-bot'" >> ~/.bashrc

# Информация о завершении
echo ""
echo "=================================================="
log "✅ Настройка завершена успешно!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Загрузите файлы бота в ~/highrise-bot/"
echo "2. Отредактируйте config.json"
echo "3. Запустите бота: bot-start"
echo ""
echo "🛠️ Команды управления:"
echo "  bot-start     - Запустить бота"
echo "  bot-stop      - Остановить бота"
echo "  bot-restart   - Перезапустить бота"
echo "  bot-status    - Статус бота"
echo "  bot-logs      - Логи в реальном времени"
echo "  bot-logs-recent - Последние логи"
echo "  cd-bot        - Перейти в папку бота"
echo ""
echo "📁 Рабочая директория: ~/highrise-bot/"
echo "📝 Логи: sudo journalctl -u highrise-bot -f"
echo ""
echo "🔄 Перезагрузите терминал или выполните: source ~/.bashrc"
echo "==================================================" 