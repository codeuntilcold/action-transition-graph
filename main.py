import logging
from graph import Bucket, TransitionGraph
from connector import ModelConnector, ClientDisconnected
import argparse

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt="%y-%m-%d %H:%M:%S")

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--savefile", default=False)
parser.add_argument("-p", "--port", default=24000)
parser.add_argument("-r", "--smoothradius", default=5)
parser.add_argument("-h", "--hardgraph", default=False)
args = parser.parse_args()


def main():
    connector = ModelConnector(args.port)
    bucket = Bucket(stream=connector.get_stream_gen(),
                    radius=args.smoothradius)
    bone = TransitionGraph(args.hardgraph, args.savefile)

    while True:
        try:
            new_state, prev_conf, conf = bucket.drip()
            bone.update_state(new_state, prev_conf)
        except ClientDisconnected:
            logging.warning("Reset state")
            bone.reset_state()
            bucket.flush()
            continue
        except Exception as e:
            logging.error(f"Error: {e}")
            logging.error("Shut down everything")
            break

    connector.close()


if __name__ == "__main__":
    main()
