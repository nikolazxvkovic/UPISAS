import platform

from UPISAS.exemplar import Exemplar

# The scenario image is published per architecture: arm64 (Apple Silicon) or amd64 (Intel/AMD)
ARCH = "arm64" if platform.machine().lower() in ("arm64", "aarch64") else "amd64"


class RAMSES(Exemplar):
    """
    RAMSES (SEFA e-food system) reached through interface/interface.py on port 50000.
    The container started here is the load-generating scenario; RAMSES itself is
    started separately with RUN_ALL.sh.
    """
    def __init__(self, auto_start=False, container_name="simulation-scenario"):
        docker_config = {
            "name": container_name,
            "image": f"giamburrasca/scenario1:{ARCH}",
            "network": "ramses-sas-net",
            "environment": {
                "ADAPT": "0",
                "FAILURE_INJECTION_1_START": "120",
            },
        }

        super().__init__("http://localhost:50000", docker_config, auto_start)

    def start_run(self):
        self.start_container()
