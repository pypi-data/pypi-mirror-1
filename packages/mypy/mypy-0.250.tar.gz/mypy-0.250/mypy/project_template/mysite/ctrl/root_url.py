from mypy.route_render import route, render_func


@route.index
@render_func
def index():
    G.name = {
        1:1,
        2:2,
        3:3,
    }


@route.login
def login():

    return "Yx"