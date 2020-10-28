import os
import json
from enum import Enum


class subscriber:
    def __init__(self, name, ip):
        self.ip = ip
        self.name = name


class deployment_opts:
    def __init__(self, opts):
        self.machine = opts['machine']
        self.run_dir = opts['run_dir']
        # more options here


class broker_states(Enum):
    offline = "Offline"
    configured = "Configured"
    online = "Online"


class broker:
    def __init__(self, cfg_path=None):
        self.name = None
        self.cfg_path = None
        self.subscribe_to = []
        self.deployment_opts = None
        self.cfg_data = None

        # parse configuration if supplied
        if cfg_path:
            self._parse(cfg_path)

        # state machine properties
        self._broker_pid = None
        self._broker_state = broker_states.offline
        self._start_command = None

    def _parse(self, cfg_path):
        self.cfg_path = cfg_path
        self.cfg_data = None
        if not os.path.exists(self.cfg_path):
            print("Config File does not exist!")
            return False
        with open(self.cfg_path, "r") as read_file:
            self.cfg_data = json.load(read_file)

        deploy_opts = self.cfg_data['deployment']
        self.deployment_opts = deployment_opts(deploy_opts)
        return True

    def start_broker(self):
        if self._broker_state is not broker_states.offline:
            print("Broker is not offline. Can't start it.")
            return False

        self._configure()
        self._start()
        return True

    def stop_broker(self):
        if self._broker_State is not broker_states.online:
            print("Broker is not online. Can't stop it.")
        self._stop()

    def reconfigure_broker(self):
        self._configure()
        self._start()

    def generate_start_command(self):
        return ""

    def _configure(self):
        if not self._parse(self.cfg_path):
            self._abort()
        #  check state transition offline -> configured
        self._broker_state = broker_states.configured
        print("Broker configured")
        return True

    def _abort(self):
        print("configure failed. Aborting")
        self._broker_state = broker_states.offline
        return True

    def _start(self):
        # start broker
        self._broker_pid = self.generate_start_command()
        self._broker_state = broker_states.online
        return True

    def _stop(self):
        # kill self._broker_pid
        self._broker_State = broker_states.offline
        return True

    def _get_state(self):
        return self._broker_state

    def _get_pid(self):
        return self._broker_pid
