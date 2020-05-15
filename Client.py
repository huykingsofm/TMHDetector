from Tcp import Tcp
import json
import argparse
import random

def __solver__(conn, addr, data, **kwargs):
    data = json.loads(data)
    kind = data["kind"]
    if kind == "notify":
        content = data["data"]

        if "end" not in data:
            end = "\n"
        else:
            end = data["end"]

        if "level" not in data:
            level = None
        else:
            level = data["level"]

        if level is not None:
            print("|--" + "----" * level + " ", end = "", flush= True)
        print(content, end = end, flush= True)

    if kind == "progress":
        current = data["current"]
        maximum = data["maximum"]
        if current > maximum:
            raise Exception("current must be lower than maximum")

        n = len(str(maximum))
        content = "[{:{}d}/{:{}d}]".format(current, n, maximum, n) + "\b" * (n * 2 + 3)
        print(content, end = "", flush= True)

    if kind == "result":
        print("This account is {}".format(data["data"]))
        if "client" not in kwargs:
            raise Exception("Expected client parameter")
        client = kwargs["client"]
        if client.output is not None:
            with open(client.output, mode = "w") as f:
                f.write(data["data"])

def main(args):
    try:
        client = Tcp.TcpClient(__solver__, error_log= False)
        client.output = args.output
        client.connect(args.ip, args.port)
        if args.status == "default":
            args.status = str(random.randint(1000000000, 9999999999))
        client.socket.send(json.dumps({"fb_id" : args.id, "uid": args.status}).encode())
        client.start()
    except Exception as e:
        print(str(e))
        return

    while client.isconnect():
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description= 
        "A tool which detect a facebook account whether fake or not"
        )
    parser.add_argument(
        "id",
        help= "a link or id of the facebook account"
    )

    parser.add_argument(
        "--ip", 
        help= "Server's ip (by default 127.0.0.1)",
        default= "127.0.0.1"
    )

    parser.add_argument(
        "--port",
        help= "Server's port (by default 12345)",
        default= 12345,
        type= int
    )

    parser.add_argument(
        "-o", "--output",
        help= "Export result to file",
        default= None
    )

    parser.add_argument(
        "-s", "--status",
        help= "status file",
        default= "default"
    )

    args = parser.parse_args()

    main(args)