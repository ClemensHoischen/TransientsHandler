import voeventparse as vp


def verify_alert_format(alert):
    format_ok = False
    # if not vp.valid_as_v2_0(alert):
    #     print("Alert is not compliant with VoEvent2.0 standard! Aborting.")
    # else:
    #     format_ok = True
    format_ok = True
    return format_ok


def verify_alert_type(alert, allowed_alert_types):
    alert_allowed = False

    for allowed_type in allowed_alert_types:
        if allowed_type in alert.ivorn:
            alert_allowed = True

    return alert_allowed


def verify_alert_unique(alert):
    return True


def verify_alert(alert, allowed_alert_types):
    alert_type_allowed = verify_alert_type(alert, allowed_alert_types)
    alert_format_allowed = verify_alert_format(alert)
    alert_unique = verify_alert_unique(alert)
    # nofy_on_received()
    return (alert_format_allowed and alert_type_allowed and alert_unique)
