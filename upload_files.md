# 📤 Загрузка файлов на VPS

## Способ 1: SCP (рекомендуемый)

```bash
# Из папки new_bot на вашем компьютере
scp -r . ubuntu@YOUR_VM_IP:~/highrise-bot/
```

## Способ 2: SFTP

```bash
# Подключение
sftp ubuntu@YOUR_VM_IP

# Загрузка файлов
put -r . /home/ubuntu/highrise-bot/
```

## Способ 3: Вручную через SSH

```bash
# Подключение
ssh ubuntu@YOUR_VM_IP

# Создание файлов
nano main.py
# Вставьте содержимое main.py

nano run_forever.py
# Вставьте содержимое run_forever.py

nano config.json
# Вставьте содержимое config.json
```

## Способ 4: Git (если есть репозиторий)

```bash
# На VPS
git clone https://github.com/your-username/your-repo.git
cd your-repo/new_bot
```

## Проверка файлов

```bash
# Проверьте, что все файлы на месте
ls -la ~/highrise-bot/
``` 