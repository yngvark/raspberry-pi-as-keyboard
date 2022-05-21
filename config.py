def get_config(test_mode):
    config = dict()

    if test_mode:
        config["test_mode"] = True
        config["syslog_file"] = "syslog"
    else:
        config["test_mode"] = False
        config["syslog_file"] = "/var/log/syslog"

    return config