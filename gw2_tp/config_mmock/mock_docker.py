import docker
from pathlib import Path

config_path = Path(__file__).resolve().parent

client = docker.from_env()
container = client.containers.run("jordimartin/mmock",
                                  detach=True,
                                  volumes={config_path: {'bind': '/config'}},
                                  ports={'8082': 8082, '8083': 8083})
# container.stop()
# container.remove()
