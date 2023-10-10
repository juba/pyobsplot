from tempfile import mkdtemp
from jupyterlab.galata import configure_jupyter_server

c = globals()["c"]

configure_jupyter_server(c)

c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.root_dir = mkdtemp(prefix="galata-test-")
c.ServerApp.password = ""
c.ServerApp.disable_check_xsrf = True
c.LabApp.expose_app_in_browser = True
