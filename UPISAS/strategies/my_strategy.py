import time

from UPISAS.strategy import Strategy

SERVICE_ID = "RESTAURANT-SERVICE"
# Statuses that mean an instance is serving or about to; anything else (incl. no snapshot) is dead
ALIVE_STATUSES = {"ACTIVE", "BOOTING"}
# Keep a spare instance so the service survives losing one while a replacement boots
TARGET_INSTANCES = 2
# A new instance needs time to boot and register; don't add another one meanwhile
ADD_COOLDOWN_S = 60


class MyStrategy(Strategy):

    def __init__(self, exemplar):
        super().__init__(exemplar)
        self.last_add_time = None
        # Remembered from earlier polls: the service vanishes from the architecture once its last instance dies
        self.implementation = "restaurant-service"

    def analyze(self):
        latest = self.knowledge.monitored_data["services"][-1]
        service = latest.get(SERVICE_ID)
        if service is None:
            print(f"[Analysis]\t{SERVICE_ID} not in architecture, all instances lost")
            alive = []
        elif service["snapshot"] is None:
            # The probe call failed (it times out under load): no data is not the same as all dead
            print(f"[Analysis]\t{SERVICE_ID}: probe snapshot unavailable, skipping this poll")
            return False
        else:
            self.implementation = service["currentImplementationId"]
            instances = service["instances"]
            snapshot = service["snapshot"]
            status_by_id = {s.get("instanceId"): s.get("status") for s in snapshot}
            alive = [i for i in instances if status_by_id.get(i) in ALIVE_STATUSES]
            print(f"[Analysis]\t{SERVICE_ID}: {len(alive)} alive of {len(instances)} "
                  f"listed, statuses {status_by_id}")

        self.knowledge.analysis_data = {
            "implementation": self.implementation,
            "alive": alive,
        }
        return len(alive) < TARGET_INSTANCES

    def plan(self):
        if self.last_add_time is not None and time.monotonic() - self.last_add_time < ADD_COOLDOWN_S:
            print("[Plan]\t\treplacement already starting, waiting")
            return False

        alive = self.knowledge.analysis_data["alive"]
        missing = TARGET_INSTANCES - len(alive)
        self.knowledge.plan_data = {
            "operation": "addInstances",
            "parameters": {
                "serviceImplementationName": self.knowledge.analysis_data["implementation"],
                "numberOfInstances": missing,
            },
        }
        self.last_add_time = time.monotonic()
        print(f"[Plan]\t\tadding {missing} instance(s) of {self.knowledge.analysis_data['implementation']}")
        return True
