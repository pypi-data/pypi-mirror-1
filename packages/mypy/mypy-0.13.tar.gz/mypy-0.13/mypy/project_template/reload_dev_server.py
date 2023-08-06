def start():
    from dev_server import run
    run('0.0.0.0',9888)

from mypy.reload_server import auto_reload
auto_reload(start)