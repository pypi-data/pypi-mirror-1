import httpencode

def app(environ, start):
    headers = [("Content-type", "text/html")]
    start("200 OK", headers)

    h = httpencode.HTTP()
    data = h.request("http://localhost:8080/?size=1", output="python", wsgi_request=environ)
    return [str(data)]
    
def make_app(global_config, **local_conf):
    return app
