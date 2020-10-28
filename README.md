# TransientsHandler
TransientsHandler code for ACADA of CTA.
It is responsibilities are:
- Receiving science alerts from external scientific installations as well as the internal science alert generation pipeline
- Processing the alert according to science configurations. Evaluating slection cuts as well as observability parameters
- Propose changes of the current or intermediate schedule of observations
- Publish information on triggered observations as well as transients detected by the SAG

# Warning:
- The Transients Handler code is in an early development phase and larger changes to the code, it's structure and data models are to be anticipated.
- No ACS functionality is implemented yet.
- No interfaces to other ACADA sub-systems are implement yet.

# Requirements:
- python 3.7
- all packages listed in requirements.txt
- the broker that is being supported for now is Comet (https://comet.transientskp.org/en/stable/). This software is not included in the page and needs to be installed manually (cloned according to the instructions on the page) in order to be able to add the plugin that is supplied under broker_system/plugins/comet_broer_plugin.py


# Installation and Deployment:
- There is no full deployment strategy yet
- The location of the science configurations can be set via the th_site_config.json in the main directory of the TH.
- The broker can be started using startup_scripts/start_comet_broker.py
- test alerts to play around with are supplied under tests/test_voevent_alerts. Running one of these alerts trhought the TH can be done using tests/process_swift_alert.py


# Main aspects of the modules:
- broker_system:
	Contains entry_point which is used in demonstrations as well as for alerts received via the comet broker. This broker is configured via the comet_broker_cfg.json configuration provided in broker_configurations.

- communicator:
	Mainly provides the functionality to compule alert_summaries for now.

- alert_processor:
	This is the heart of the TH. The processing_manager handles the different processing steps, calulcation of obsevation windows by observation_windows and evalulates the cuts as specified in the science configurations.

- data_models and data_models/parsers:
	This contains the object definitions for the data models that are being used trhought the TH as well as the parsers that generate these TH internal objects from the input provided (e.g. sicnec_config and scince_config_parser)

- scinece_configurations:
	A set of science configurations are provided to display different scenarios for demonstration and development. These are in simple .json format for now.
