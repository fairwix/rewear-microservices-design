# Соответствие ТЗ

Основание: [задание](assignment.txt). Результат: [отчёт](report.md).

| Условие | Где выполнено |
|---|---|
| Титульный лист | Начало: проект, ФИО, группа, дата |
| 3–5 микросервисов | **Отклонение:** шесть — Catalog, Cart, Order, Notification, Auth, Image; требуется согласование |
| Одна машина, database per service | §2.4 и §4.1: Compose/Minikube, шесть отдельных PostgreSQL |
| Sync между сервисами | §2.2, §4.2: семь HTTP endpoints |
| Async через broker | §4.4: Catalog→RabbitMQ→Cart; Cart/Order→RabbitMQ→Notification |
| 5–7 функций, 2–3 user flows, out of scope | §1: семь функций, три сценария и границы |
| Consistency, sync/async и причины | §2.1–2.2, §5 |
| Latency <100 мс / фон >1 с, нагрузка/масштабирование | §2.3 |
| Диаграмма: ответственность, типы/владение БД, broker/cache/gateway, подписи/стрелки | §3: PNG; SVG и Mermaid |
| Entities с 3–7 полями, связи и ownership | §4.1 |
| 5–7 межсервисных endpoints: caller/method/path/request/response | §4.2: ровно семь; HTTP клиента и WS отдельно §4.3/4.5 |
| Декомпозиция, альтернативы, сбои сервисов/broker/БД и решения | §5: сага, retries, outbox, дедупликация, кеш, решение по breaker |
| Форматы сдачи | Markdown и встроенная PNG-диаграмма; C4 опционален |

## Согласованные правки

| Правка | Реализация в проекте |
|---|---|
| Корзина видит бронирование другими покупателями | Catalog events → очередь Cart → персональные события → Notification/WS; при входе live HTTP к Catalog (§4.4) |
| Cart тоже использует RabbitMQ, бронь при оформлении | CartItemAdded ≠ бронь; OrderReserved после Catalog reserve (§4.4) |
| Отдельный Auth, admin/customer | §2.5; один Auth DB, server-side роль и ownership; admin create/update; Image upload/get |
| Не более 10 вещей | FR-4, атомарная проверка лимита Cart (§4.2) |
| Что/кому/когда отправили | Notification/UserStream/DeliveryAttempt (§4.1); sent_at не равно прочтению |
| Без polling для уведомлений; WebSocket вместо SSE | LISTEN/NOTIFY outbox, RabbitMQ basicConsume, SignalR только WebSockets, Resume/ACK (§4.4–4.5) |
| Loki и Grafana / observability | §2.7: OTLP, Loki/Grafana, трейсы/метрики и корреляция |
| Кеш первой страницы | §2.6: только общий page=1 без фильтров, TTL 60 с, invalidation/fallback |
| Главная и пресеты поиска | FR-2: сохранённые CatalogPage/SearchPreset, page_id/preset_id |
| S3 и CDN | §2.6: отдельный Image с image_db и SeaweedFS; браузер→Nginx-кеш→Image→S3, без распределённого CDN |

Документ описывает проектирование; код, манифесты, измерения и облачное развёртывание не выдаются за уже выполненные работы.
