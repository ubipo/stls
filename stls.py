
if __name__ == "__main__":
    import os, sys

    # Add current dir to system path to be able to import from stls
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import stls
from stls import Server


def run(ip = stls.DEF_IP, port = stls.DEF_PORT):
    try:
        print("=== stls - Sel TCP Logging Server ===")
        server = Server(ip, port)
        server.init()
        server.serveForever()
    except KeyboardInterrupt:
        exit(0)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', '--ip', dest='ip', type=str, default=stls.DEF_IP,
                        help=f"ip of listening socket (default: {stls.DEF_IP})")
    parser.add_argument('-p', '--port', dest='port', type=int, default=stls.DEF_PORT,
                        help=f"port of listening socket (default: {stls.DEF_PORT})")

    args = parser.parse_args()

    run(args.ip, args.port)


if __name__ == "__main__":
    main()
