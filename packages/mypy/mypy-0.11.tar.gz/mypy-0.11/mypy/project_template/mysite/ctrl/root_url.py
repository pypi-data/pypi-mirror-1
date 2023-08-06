from mypy.route_render import route,render_func

@route.index
@render_func
def index():
    pass


@route.login
def login():
    return "Yx"