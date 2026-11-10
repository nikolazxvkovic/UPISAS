from UPISAS.exemplar import Exemplar


class RAMSES(Exemplar):
    """
    RAMSES (SEFA e-food system) reached through interface/interface.py on port 50000.
    The container started here is the load-generating scenario; RAMSES itself is
    started separately with RUN_ALL.sh.
    """
    def __init__(self, auto_start=False, container_name="simulation-scenario"):
        docker_config = {
            "name": container_name,
            "image": "giamburrasca/scenario1:arm64",
            "network": "ramses-sas-net",
            "environment": {
                "ADAPT": "0",
                "FAILURE_INJECTION_1_START": "120",
            },
        }

        super().__init__("http://localhost:50000", docker_config, auto_start)

    def start_run(self):
        self.start_container()
