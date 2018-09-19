# Copyright (c) 2018, NVIDIA CORPORATION. All rights reserved.
# See file LICENSE for terms.

import call_myucp as ucp
import time
import argparse

def notify_completion(what_completed):
    print(what_completed)

def send_recv(msg_log, is_server, is_cuda):
    ucp.barrier()
    buffer_region = ucp.buffer_region()
    if is_cuda:
        buffer_region.alloc_cuda(1 << msg_log)
    else:
        buffer_region.alloc_host(1 << msg_log)
    msg = ucp.ucp_msg(buffer_region)
    if is_server:
        msg.set_mem(0, 1 << msg_log)
        msg.send(1 << msg_log)
    else:
        msg.set_mem(1, 1 << msg_log)
        msg.recv(1 << msg_log)
    msg.wait()
    errs = 0
    if is_server:
        errs = msg.check_mem(0, 1 << msg_log)
        print(errs)
    else:
        errs = msg.check_mem(0, 1 << msg_log)
        print(errs)

    ucp.barrier()

    if is_server:
        msg.set_mem(1, 1 << msg_log)
        msg.recv(1 << msg_log)
    else:
        msg.set_mem(0, 1 << msg_log)
        msg.send(1 << msg_log)
    msg.wait()
    errs = 0
    if is_server:
        errs = msg.check_mem(0, 1 << msg_log)
        print(errs)
    else:
        errs = msg.check_mem(0, 1 << msg_log)
        print(errs)

    if is_cuda:
        buffer_region.free_cuda()
    else:
        buffer_region.free_host()

max_msg_log = 23

parser = argparse.ArgumentParser()
parser.add_argument('-s','--server', help='enter server hostname', required=False)
args = parser.parse_args()

## show values ##
print ("Server name: %s" % args.server )

## initiate ucp
init_str = ""
is_server = True
if args.server is None:
    is_server = True
    ucp.init(init_str.encode())
    print("Server Initiated")
else:
    init_str = args.server
    is_server = False
    ucp.init(init_str.encode())
    print("Client Initiated")

## setup endpoints
ucp.setup_ep()
ucp.barrier()

ucp.set_callback(notify_completion)

is_cuda = False
send_recv(max_msg_log, is_server, is_cuda)

is_cuda = True
send_recv(max_msg_log, is_server, is_cuda)

ucp.destroy_ep()
ucp.fin()

if args.server is None:
    print("Server Finalized")
else:
    print("Client Finalized")
