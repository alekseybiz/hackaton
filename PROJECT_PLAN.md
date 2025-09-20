## Проектный план: сервис анализа количества и длительности полётов БПЛА по регионам РФ

Документ фиксирует архитектуру, стек, модель данных, API и этапы реализации по ТЗ. При расхождениях с финальной редакцией ТЗ приоритеть — требования ТЗ; правки вносятся в этом файле через PR.

### Цели
- **Аналитика по регионам**: количество полётов, суммарная/средняя длительность, распределения по времени.
- **Интерактивная карта**: тепловая карта/кластеризация точек и визуализация маршрутов полётов.
- **Импорт данных**: загрузка файлов (CSV/XLSX/JSON) и/или источники API, валидация и протокол ошибок.
- **Экспорт/отчётность**: выгрузка агрегатов и списков полётов.

### Высокоуровневая архитектура
- **Frontend**: React + TypeScript, Vite, Ant Design; карты — MapLibre GL JS; графики — Apache ECharts.
- **Backend (API)**: FastAPI (Python 3.11), SQLAlchemy 2, Pydantic v2, Alembic; веб‑сервер Uvicorn/Gunicorn.
- **Фоновые задачи/ETL**: Celery + Redis; пайплайны загрузки, очистки, геопривязки и агрегаций.
- **Хранилище**: PostgreSQL 16 + PostGIS (гео); TimescaleDB для партиционирования/тайм‑серий при больших объёмах.
- **Объектное хранилище**: MinIO/S3 для исходных файлов и экспортов.
- **Аутентификация/авторизация**: Keycloak (OIDC) + JWT; RBAC (admin, analyst, viewer). Возможна интеграция с внешним IdP.
- **Наблюдаемость**: Prometheus + Grafana (метрики), Loki (логи), Sentry (ошибки), OpenTelemetry (трейсы).
- **Деплой**: Docker Compose (dev), Kubernetes + Helm (prod), GitHub Actions (CI/CD).

### Поток данных (ETL)
1) Загрузка источников в «сырой» слой (`raw_event`) + запись метаданных загрузки (`upload`).
2) Валидация: типы/форматы, координаты (EPSG:4326), дедупликация.
3) Геопривязка: пересечение точек/маршрутов с полигонами субъектов РФ → `region_id`.
4) Реконструкция сущности `flight` из точек (разрыв N минут ⇒ новый полёт). Отсев шумов по длительности/длине.
5) Агрегации: `daily_region_stats`, `hourly_region_stats`, данные для тепловых карт.
6) Публикация через API, кеширование горячих витрин.

### Основные сущности БД
- `region(id, name, okato, polygon geometry(MultiPolygon,4326))`
- `operator(id, name, inn, org_type)`
- `uav(id, model, weight_class, operator_id)`
- `upload(id, source, file_uri, status, errors jsonb, created_at)`
- `raw_event(id, upload_id, ts timestamptz, geom geometry(Point,4326), uav_id, payload jsonb)`
- `flight(id, uav_id, operator_id, start_ts, end_ts, duration_sec, path geometry(LineString,4326), region_id)`
- `flight_point(id, flight_id, ts, geom)` — опционально для хранения треков
- `daily_region_stats(date, region_id, flights_cnt, avg_duration_sec, total_duration_sec)`
- `hourly_region_stats(hour_ts, region_id, flights_cnt)`

Индексация: GiST на геометрии, BRIN/GiST по времени на больших таблицах, GIN на `payload`; партиционирование `raw_event`/`flight_point` по месяцу.

### API (черновой список)
- `GET /reference/regions`
- `GET /analytics/summary?region_id&from&to`
- `GET /analytics/time-series?region_id&interval=day|hour&from&to`
- `GET /analytics/heatmap?region_id&from&to` — GeoJSON для карты
- `GET /flights?region_id&from&to&page&page_size`
- `GET /flights/{flight_id}` — маршрут, длительность, оператор
- `POST /uploads` — загрузка файла; `GET /uploads/{id}/status` — прогресс и протокол
- `GET /exports/analytics.csv` — выгрузка агрегатов

### Фронтенд (ключевые экраны)
- Карта РФ: фильтры по дате/времени/региону, тепловая/кластеризация, просмотр маршрутов.
- Дашборд: количество полётов, средняя/суммарная длительность, пики по часам.
- Список полётов и карточка полёта; экспорт в CSV.
- Экран загрузок с журналом ошибок.
- Вход/выход, роли и доступы.

### Нефункциональные требования
- Производительность: p95 < 300 мс по витринам; тяжёлые запросы — асинхронно/предрасчёт.
- Масштабирование: шардирование по времени, партиционирование, TimescaleDB, кэширование.
- Безопасность: TLS, RBAC, аудит действий; при необходимости Row‑Level Security по регионам.

### Структура репозитория
```text
/infra
  docker-compose.yml
  k8s/helm
/backend
  app/main.py
  app/api/{analytics,flights,uploads,reference}.py
  app/services/{ingest,flights,stats}.py
  app/db/{base.py,session.py,migrations}
/frontend
  src/pages/{Map,Dashboard,Flights,Uploads,Login}.tsx
  src/components/*
  src/api/*
/etl
  pipelines/{ingest_csv.py,build_aggregates.py}
  jobs/{celery.py,beat_schedule.py}
```

### План MVP (≈2 недели)
Неделя 1:
- Инициализация репозитория, Docker Compose (Postgres+PostGIS, Redis, MinIO, API, Frontend).
- Миграции БД, загрузка полигонов регионов.
- Ингест CSV/Excel → `raw_event` + протокол ошибок.
- Реконструкция `flight` и витрина `daily_region_stats`.

Неделя 2:
- Реализация API: `reference`, `analytics/summary`, `time-series`, `flights`, `uploads`.
- Фронтенд: карта (тепловая/кластера), дашборд, список полётов.
- Аутентификация (Keycloak/JWT), базовые роли.
- Экспорт CSV, базовый мониторинг, CI (lint/test/build) и автосборка контейнеров.

### Ключевые алгоритмы
- Разбиение треков на полёты: сортировка по времени; если разрыв между точками > N минут (5–10) — новый полёт.
- Длительность: `duration = end_ts - start_ts`; фильтр шумов (порог по длительности/длине).
- Привязка к региону: по доминирующему времени в полигоне либо по стартовой точке.

### Первоначальные команды (dev)
```bash
docker compose up -d            # поднять инфраструктуру
alembic upgrade head            # миграции БД
uvicorn app.main:app --reload   # запуск backend
pnpm dev                        # запуск frontend
```

### Риски и предположения
- Качество исходных данных (точность координат/времени) может потребовать дополнительных правил очистки.
- При объёмах >100 млн событий/год обязательно партиционирование и витрины; on-demand аналитика только по агрегатам.
- Точные SLA/безопасность/обязательные интеграции уточняются по ТЗ; изменения будут отражены в этом плане.


