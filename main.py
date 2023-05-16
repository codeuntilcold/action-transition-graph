import logging

from graph import Bucket, TransitionGraph
from connector import ModelConnector, ClientDisconnected

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt="%y-%m-%d %H:%M:%S")


def main():
    connector = ModelConnector()
    bucket = Bucket(stream=connector.get_stream_gen(), radius=15)
    bone = TransitionGraph()

    while True:
        try:
            new_state, prev_conf, conf = bucket.drip()
            bone.update_state(new_state, prev_conf)
        except ClientDisconnected:
            logging.warning("Reset state")
            bone.reset_state()
            bucket.flush()
            continue
        except Exception:
            logging.error("Shut down everything")
            break

    connector.close()


if __name__ == "__main__":
    main()
