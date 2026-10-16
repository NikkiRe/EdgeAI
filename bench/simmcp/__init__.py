"""sim-mcp — эмулятор помещения для стенда EdgeCtx.

MCP-сервер (mcp SDK, streamable HTTP на localhost) с инвентарём из заголовка дня daygen, истинным
состоянием, проигрыванием событий дня по часам агента/реплеера (POST /control/clock), уведомлениями
notifications/resources/updated, инструментами оценки answer/refuse и журналом JSONL.
CLI: ``python -m bench.simmcp --day day.jsonl --port 18090``.
"""
from .server import SimMCP, build_app
from .world import World

__all__ = ["SimMCP", "World", "build_app"]
