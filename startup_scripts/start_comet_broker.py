import sys
sys.path.append("/Users/hoischen/CTA/github/TransientsHandler")

from broker_system.brokers import comet_broker


def main():
    comet_cfg = "/Users/hoischen/CTA/TransientsHandler/configurations/broker_configurations/comet_broker_cfg.json"
    comet = comet_broker.comet_broker(comet_cfg)
    comet.start_broker()


if __name__ == '__main__':
    main()
