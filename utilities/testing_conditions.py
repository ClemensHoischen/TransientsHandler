
class TestingConditions:
    def __init__(self, test_received_time):
        self.test_received_time = test_received_time

    def apply_test_conditions_to_scientific_alert(self, sci_alert):
        sci_alert.alert_received_time = self.test_received_time
        sci_alert.alert_authored_time = self.test_received_time  # - timedelta(seconds=10)
        sci_alert.testing_conditions_applied = True


# Class that holds the resutls that are expected from the processing for a given alert and science configuration.
class ExpectedResults:
    def __init__(self):
        pass


# compares the expected results with the actural results of the processing
def validate_test_case():
    pass
