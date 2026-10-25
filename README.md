# EdgeAI

AI-агент для IoT и робототехники на Go. Подключает оборудование через MCP, хранит контекст и память в SQLite, управляет задачами и обращениями к внешней LLM.

Локальные правила обрабатывают события без ожидания модели. LLM подключается для запросов, которым нужен дополнительный контекст или вызов инструментов. Для проверки есть симулятор датчиков, стенд с ограничениями ресурсов и цифровой двойник робота в Gazebo.

Дипломный проект ИТМО «Разработка ИИ-агента для приложений граничного искусственного интеллекта». Runtime агента называется EdgeCtx.

## Возможности

- Подключение датчиков и исполнительных устройств Linux через MCP.
- Обработка событий, приоритеты задач и лимиты обращений к LLM.
- Контекст оборудования и пользователя, память в SQLite.
- Повторы запросов и восстановление соединений после сбоев.
- Интеграция робота через ROS 2 и rosbridge, проверка команд управления.
- Пульт оператора: состояние робота, телеметрия, жесты, безопасность и воспроизведение прогонов.
- Стенд сравнения с PicoClaw и nanobot на сценариях CASAS/MASSIVE: вызовы LLM, токены, трафик, задержки, память и CPU.

## Структура

| Каталог | Назначение |
|---|---|
| [agent](agent/) | EdgeCtx: события, планировщик, контекст, память и MCP-клиент |
| [hwmcp](hwmcp/) | Датчики и приводы: IIO, hwmon, 1-Wire, GPIO, проверка команд |
| [cammcp](cammcp/) | Камера и детектор движения |
| [robotmcp](robotmcp/) | MCP-адаптер робота поверх rosbridge |
| [neurobot](neurobot/README.md) | Робот NeuroChip: safety_gate, исполнитель, запуск под systemd, MCP для агента, цифровой двойник |
| [neurobot/ui](neurobot/ui/) | Пульт оператора |
| [bench](bench/) | Генерация и повтор сценариев, аналоги, метрики, эмуляция платы и датчиков |
| [sysmon](sysmon/) | Память, CPU и IO процессов и cgroup v2 |
| [monitor](monitor/), [harness](harness/) | Проверка трасс и статистика |
| [scripts](scripts/) | Запуск стендов Linux, ROS 2 и Gazebo |
| [reference](reference/) | Python-прототипы, фикстуры и снимок цен, с которыми сверяется код |
| [data](data/) | Выборки CASAS и MASSIVE для сценариев рабочего дня |
| [docs](docs/) | Сенсорное ядро, монитор трасс, симулятор робота, журнал решений |

## Что проверено и где

Все числа, снятые на стенде, — ориентир, а не результат работы на устройстве.

В симуляции и эмуляции (Mac и ВМ Lima с Ubuntu 24.04 arm64):

- тесты модулей Go и Python, сквозные тесты агента с настоящими hw-mcp, cam-mcp и sim-mcp (`bench/tests`);
- «минимальная плата»: агент и hw-mcp в одном юните systemd с лимитами cgroup v2 — 64 МиБ памяти, 25% CPU одного ядра, сеть 3G через `tc netem`; датчики — симулятор sysfs (`bench/sysfsim`) с модулем ядра `gpio-sim`;
- GPIO uAPI v1 и v2 на `gpio-sim` (ядро 6.8), пропажа и возвращение датчика на `iio_dummy`;
- обрыв связи с LLM и падение MCP-сервера: отложенные пробуждения уходят одним ходом, сервер переподключается;
- камера: синтетическая сцена и виртуальная камера ядра `vivid`;
- робот: TurtleBot3 и Nav2 в Gazebo ([docs/robot_sim.md](docs/robot_sim.md)) и цифровой двойник робота NeuroChip в Gazebo Harmonic с ROS 2 Jazzy — safety_gate, исполнитель, запуск под systemd, прогоны A0/A1, пульт оператора в живом режиме;
- LLM: заглушка `bench/mockllm` с OpenAI-совместимым API; трассы прогонов проверяет независимый монитор (`monitor/`).

На реальном оборудовании в этой версии не проверялись: Jetson Nano (JetPack 4.6, ядро 4.9), SD-карта, настоящие датчики, USB-камера, робот лаборатории (на нём ROS 2 Foxy; код для него проверен тестами логики под Python 3.8 и на двойнике с ROS 2 Jazzy) и реальная LLM (RouterAI). Подробности — в README модулей (разделы о проверках) и в [docs/SENSOR_CORE.md](docs/SENSOR_CORE.md).

YOLO, SNN, исходный код робота и его MCP-серверы принадлежат лаборатории NeuroChip и в репозиторий не входят, как и наши патчи к ним. Собственная часть проекта: агент, MCP-интеграции, обработка событий, исполнение команд, наблюдаемость и стенд экспериментов.

## Эталоны: reference/

Python-прототипы и фикстуры, с которыми сверяется основной код: инвентаризация sysfs и синтетическое дерево `/sys` (`reference/sysfs`, паритет с hw-mcp), шлюз приводов (`reference/gate`, эталонные потоки решений для hw-mcp и монитора), модель стоимости истории (`reference/history_cost`, перенесена в `bench/costmodel` с проверкой паритета), выгрузка MASSIVE (`reference/massive`) и снимок цен RouterAI на 06.10.2026 (`reference/prices`).

## Запуск

Нужны Go 1.27, Python 3.12 и `uv`. Команды выполняются из корня проекта.

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements-dev.txt
export PYTHONDONTWRITEBYTECODE=1

for m in agent hwmcp cammcp robotmcp sysmon bench/board/cpubench; do (cd "$m" && go test ./...) || break; done

.venv/bin/python -m pytest -q -p no:cacheprovider bench/tests monitor/tests harness/tests
.venv/bin/python -m pytest -q -p no:cacheprovider bench/baselines/tests
.venv/bin/python -m bench.sensors --out /tmp/sensor-smoke
```

Робот NeuroChip и пульт оператора ([обзор](neurobot/README.md)):

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider neurobot
.venv/bin/python -m neurobot.ui serve --bundle neurobot/ui/samples/demo_hall.json.gz   # http://127.0.0.1:18120/
```

Тесты, которым нужны ROS 2, Gazebo или PyTorch, вне ВМ пропускаются. Тесты, которым нужны код или конфиг лаборатории NeuroChip и патчи к ним, без этих файлов тоже пропускаются, с указанием причины.

Стенды робота требуют Linux с ROS 2 Jazzy и Gazebo Harmonic; на Mac они работают в ВМ Lima (`scripts/sim`, [docs/robot_sim.md](docs/robot_sim.md)). Эмуляция слабой платы — [bench/board](bench/board/README.md).

Архив CASAS скачивается по `data/casas/PROVENANCE.txt`. Материалы и веса лаборатории NeuroChip, сборки и артефакты прогонов в репозиторий не входят. Ключи API и токены в репозитории не хранятся.

## Документация

- [Сенсорное ядро: что сделано и проверено](docs/SENSOR_CORE.md)
- [Журнал технических решений](docs/DECISIONS.md)
- [Робот NeuroChip: обзор, проверки и ограничения](neurobot/README.md)
- [Монитор трасс агента и журнала шлюза](docs/monitor.md)
- [Симулятор робота: ROS 2, Gazebo, TurtleBot3](docs/robot_sim.md)
- README модулей: [agent](agent/README.md), [hwmcp](hwmcp/README.md), [cammcp](cammcp/README.md), [robotmcp](robotmcp/README.md), [sysmon](sysmon/README.md), [bench/board](bench/board/README.md), [neurobot/sim/twin](neurobot/sim/twin/README.md), [neurobot/safety](neurobot/safety/README.md), [neurobot/deploy](neurobot/deploy/README.md), [neurobot/ui](neurobot/ui/README.md)
