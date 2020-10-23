import os
from broker_system.brokers.broker_base import broker


class remote_broker:
    ''' container class to keep the remote brokers that the TH subscribes
    to for science alerts. fed from the broker configuration. '''
    def __init__(self, name, ip):
        self.ip = ip
        self.name = name

    def __str__(self):
        return "remote %s -- ip: %s" % (self.name, self.ip)


class allowed_alert_type:
    ''' container class to keep the allowed alert types that
    are specified in the config files '''
    def __init__(self, name, alert_ids):
        self.ids = alert_ids
        self.name = name

    def __str__(self):
        return "%s -- identified by: %s" % (self.name, self.ids)


class comet_broker(broker):
    ''' actual broker class implementing the start_broker function.
    inherits from the base broker class of the TH. '''
    def generate_start_command(self):
        ''' generates to the twistd comet start command using the
        options specified in the broker configuration file. '''
        comet_opts = self.cfg_data['comet_options']

        start_comm = "twistd comet -vvvvv "

        local_ivo = comet_opts["local-ivo"]
        start_comm += "--local-ivo %s " % local_ivo

        event_db = comet_opts['event_db']
        start_comm += "--eventdb %s " % event_db

        remotes_data = comet_opts["remote"]
        remotes = []
        for remote in remotes_data:
            print(remote_broker(remote, remotes_data[remote]))
            remotes.append(remote_broker(remote, remotes_data[remote]))

        for rem in remotes:
            start_comm += "--subscribe %s " % rem.ip

        allowed_type_data = comet_opts['allowed_types']
        print(allowed_type_data)
        allow = []
        for allowed_type in allowed_type_data:
            print(allowed_type_data[allowed_type])
            allow.append(allowed_alert_type(allowed_type,
                                            allowed_type_data[allowed_type]))

        start_comm += "--th_entry "
        start_comm += produce_ivorn_allowed_string(allow)

        return start_comm

    def start_broker(self):
        ''' for mini acada: override the base class which is intended as a state machine.'''
        start_comm = self.generate_start_command()
        os.chdir(self.deployment_opts.run_dir)
        print(start_comm)
        os.system(start_comm)
        pid = self.get_pid()
        print("launched the comet broker with pid: %s" % pid)
        return

    def get_pid(self):
        ''' retrieves the process id of the comet broker once it has been launched. '''
        pid_file = self.deployment_opts.run_dir + "/twistd.pid"
        with open(pid_file, "r") as f:
            pid = f.read()

        print(pid)
        return pid


def produce_ivorn_allowed_string(allow_type):
    ''' produces the option input for the comet plugin to allow
    for processing of incoming alerts. '''
    start_comm = "--th_entry-allow-types "
    for allowed in allow_type:
        print(allowed)
        id_allowed = ""
        for i, an_id in enumerate(allowed.ids):
            if i < len(allowed.ids) - 1:
                id_allowed += an_id + ","
            else:
                id_allowed += an_id + "++"
        start_comm += id_allowed

    start_comm = start_comm[:-2]
    print(start_comm)
    return start_comm
