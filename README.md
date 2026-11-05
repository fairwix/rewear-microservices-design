# ReWear — магазин винтажной одежды

Лабораторная №6: проектирование микросервисной архитектуры. Четыре сервиса: Catalog, Cart, Order и Notification; отдельные PostgreSQL, HTTP, RabbitMQ и Redis для кеша каталога. Order — бизнес-оркестратор покупки.

## Материалы

- [Отчёт по всем пунктам ТЗ](docs/report.md).
- [Диаграмма PNG](docs/diagrams/architecture.png), [SVG](docs/diagrams/architecture.svg), [Mermaid](docs/diagrams/architecture.mmd).
- [Соответствие ТЗ](docs/compliance.md), [план реализации](docs/implementation-plan.md), [задание](docs/assignment.txt).

![Архитектура](docs/diagrams/architecture.png)

План запуска: Docker Compose для разработки и Kubernetes через Minikube для демонстрации на одной машине. В репозитории готова архитектурная работа; приложение и конфигурации запуска относятся к следующему этапу.

Для повторного построения диаграммы:

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/render_diagram.py
```
