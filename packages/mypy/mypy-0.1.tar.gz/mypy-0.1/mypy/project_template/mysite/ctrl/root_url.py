from mypy.route_render import route

@route.index
def index():

    return "Y"


@route.login
def login():
    return "Yx"