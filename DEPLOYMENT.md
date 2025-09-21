## Развёртывание на одном сервере (Docker Compose)

Подходит для пилота/MVP. Для продакшена с несколькими узлами используйте Kubernetes/Helm.

### 1) Предварительно
- Linux (Ubuntu 22.04+ рекомендовано)
- Установить Docker Engine и Docker Compose Plugin
- Открыть порты: 80/443 (если будет прокси), 8000 (API), 9000/9001 (MinIO)

### 2) Клонировать репозиторий и заполнить переменные
```bash
git clone <repo_url> hackaton && cd hackaton
cp .env.example .env
# отредактируйте пароли/секреты в .env
```

### 3) Запустить инфраструктуру
```bash
cd infra
docker compose up -d --build
```
Сервисы:
- Postgres+PostGIS: localhost:5432
- Redis: localhost:6379
- MinIO: http://localhost:9000 (консоль: http://localhost:9001)
- Backend API: http://localhost:8000

### 4) Применить миграции БД
```bash
cd ../backend
docker compose -f ../infra/docker-compose.yml exec backend alembic upgrade head
```

### 5) Импорт полигонов регионов РФ
Скопируйте GeoJSON на сервер в папку `data/regions.geojson` и выполните:
```bash
docker compose -f ../infra/docker-compose.yml exec backend \
  python -m app.cli.import_regions /data/regions.geojson
```

### 6) Проверка
```bash
curl http://<SERVER_IP>:8000/health
curl http://<SERVER_IP>:8000/reference/regions
```

### 7) (Опционально) Прокси и TLS
Быстрый способ — Caddy:
```bash
sudo apt install -y caddy
sudo tee /etc/caddy/Caddyfile >/dev/null <<'C'
your.domain.com {
  reverse_proxy 127.0.0.1:8000
}
C
sudo systemctl reload caddy
```

### 8) Автозапуск после ребута (systemd unit)
```ini
[Unit]
Description=Hackaton stack
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/hackaton/infra
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```
Сохраните как `/etc/systemd/system/hackaton.service`, затем:
```bash
sudo systemctl enable --now hackaton
```

### Переменные окружения
См. `.env.example`. В проде замените пароли/секреты и закройте внешние порты БД/Redis/MinIO, проксируйте только API.


