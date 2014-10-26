import sys
import argparse
import re
import requests
import json
import os

import host

BASE_URL = "http://localhost:8080"
HEADERS = {'content-type': 'application/json'}
FUNC_MAPPER = {}
CURR_HOST = ".curr_host"

def cmd(cmd, args=[], opt_args=[]):
    FUNC_MAPPER[cmd] = {"args": args,
                        "opt_args": opt_args}
    def deco(func):
        FUNC_MAPPER[cmd]["func"] = func
        FUNC_MAPPER[cmd]["description"] = func.__doc__
        def wrapper():
            pass
        return wrapper
    return deco

def curr_host():
    global BASE_URL
    if(os.path.exists(CURR_HOST)):
        f = open(CURR_HOST)
        c_host = f.read()
        f.close()
        BASE_URL = host.HOST.get(c_host, None)
        if(BASE_URL is None):
            print "The host %s you set not in host list," \
            " use python agentctl.py host_list show avalible host" % c_host
            exit()
        print "Execute on hyper-v host: %s" % BASE_URL
    else:
        print "You should use python agentctl.py use_host <hostname> to assign a hyper-v sever"
        exit()

@cmd("host_list", args=[], opt_args=[])
def host_list(argv):
    print host.HOST

@cmd("use_host", args=["hostname"], opt_args=[])
def use_host(argv):
    f = open(".curr_host", "w")
    f.write(argv.hostname)
    f.close()

@cmd("instance_list", args=[], opt_args=[])
def instance_list(argv):
    """List instances"""
    curr_host()
    r = requests.get(BASE_URL + "/instances")
    print r.text

@cmd("image_list", args=[], opt_args=[])
def image_list(argv):
    """List images"""
    curr_host()
    r = requests.get(BASE_URL + "/images")
    print r.text

@cmd("instance_show", args=["name"], opt_args=[])
def instance_show(argv):
    """Show instance detail"""
    curr_host()
    r = requests.get(BASE_URL + "/instances/%s" % argv.name)
    print r.text

@cmd("instance_suspend", args=["name"], opt_args=[])
def instance_suspend(argv):
    """Start instance"""
    curr_host()
    r = requests.post(BASE_URL + "/instances/%s/suspend" % argv.name,
                      headers=HEADERS)
    print r.text

@cmd("instance_resume", args=["name"], opt_args=[])
def instance_resume(argv):
    """Start instance"""
    curr_host()
    r = requests.post(BASE_URL + "/instances/%s/resume" % argv.name,
                      headers=HEADERS)
    print r.text

@cmd("instance_pause", args=["name"], opt_args=[])
def instance_pause(argv):
    """Start instance"""
    curr_host()
    r = requests.post(BASE_URL + "/instances/%s/pause" % argv.name,
                      headers=HEADERS)
    print r.text

@cmd("instance_unpause", args=["name"], opt_args=[])
def instance_unpause(argv):
    """Start instance"""
    curr_host()
    r = requests.post(BASE_URL + "/instances/%s/unpause" % argv.name,
                      headers=HEADERS)
    print r.text

@cmd("instance_poweron", args=["name"], opt_args=[])
def instance_poweron(argv):
    """Start instance"""
    curr_host()
    r = requests.post(BASE_URL + "/instances/%s/poweron" % argv.name,
                      headers=HEADERS)
    print r.text

@cmd("instance_poweroff", args=["name"], opt_args=["hard"])
def instance_poweroff(argv):
    """Shutdwon instance"""
    curr_host()
    body = {"hard": False}
    if(argv.hard):
        body["hard"] = True
    r = requests.post(BASE_URL + "/instances/%s/poweroff" % argv.name,
                      data=json.dumps(body), headers=HEADERS)
    print r.text

@cmd("instance_reboot", args=["name"], opt_args=["hard"])
def instance_reboot(argv):
    """Reboot instance"""
    curr_host()
    body = {"hard": False}
    if(argv.hard):
        body["hard"] = True
    r = requests.post(BASE_URL + "/instances/%s/reboot" % argv.name,
                      data = json.dumps(body), headers=HEADERS)
    print r.text

@cmd("instance_console", args=["name"], opt_args=[])
def instance_console(argv):
    """Get instance rdp console"""
    curr_host()
    r = requests.get(BASE_URL + "/instances/%s/console" % argv.name)
    print r.text

@cmd("instance_delete", args=["name"], opt_args=[])
def instance_delete(argv):
    """Delete instance"""
    curr_host()
    r = requests.delete(BASE_URL + "/instances/%s" % argv.name)
    print r.text

@cmd("instance_create", args=[],
    opt_args=["name","cpu","mem","image","vhdext"])
def instance_create(argv):
    """Create instance"""
    curr_host()
    body = dict()
    if(argv.name):
        body["name"] = argv.name
    if(argv.cpu):
        body["cpu"] = argv.cpu
    if(argv.mem):
        body["mem"] = argv.mem
    if(argv.image):
        body["image"] = argv.image
    if(argv.vhdext):
        body["vhdext"] = argv.vhdext
    r = requests.post(BASE_URL + "/instances", data=json.dumps(body), headers=HEADERS)
    print r.text

@cmd("help", args=["action"])
def cli_help(argv):
    cmd_name = argv.action
    if cmd_name in FUNC_MAPPER.keys():
        func_info = FUNC_MAPPER.get(cmd_name)
        args = func_info["args"]
        opt_args = func_info["opt_args"]
        sub_parser = argparse.ArgumentParser(prog="agentctl %s" % cmd_name,
             description=func_info["description"],
             add_help=False)
        for i in args:
            sub_parser.add_argument(i)
        for i in opt_args:
            sub_parser.add_argument("--%s" % i, default=None)
        help_str = sub_parser.format_help()
        print re.sub("  -h, --help.+", "", help_str, flags=re.M)
    else:
        print "Only actions: %s available !" % " | ".join(FUNC_MAPPER.keys())

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        print ">> sub commands >>>>>>>"
        for i in FUNC_MAPPER.keys():
            print i
        sys.exit(0)
    if args[0] in ["-h", "--help"]:
        print "Usage: agentctl [sub_cmd] argvs..."
        print "Tips: agentctl help [sub_cmd]  to see usage of sub command"
        print "\nsub commands:"
        s = "\t" + "\n\t".join(FUNC_MAPPER.keys())
        print s	
        sys.exit(0)
    cmd_name = args[0]
    sub_arguments = args[1:]

    if cmd_name in FUNC_MAPPER.keys():
        sub_parser = argparse.ArgumentParser()
        func_info = FUNC_MAPPER.get(cmd_name)
        args = func_info["args"]
        opt_args = func_info["opt_args"]
        for i in args:
            sub_parser.add_argument(i)
        for i in opt_args:
            sub_parser.add_argument("--%s" % i, default=None)
        sub_args = sub_parser.parse_args(sub_arguments)
        print sub_args
        func = func_info["func"]
        ret = func(sub_args)
        sys.exit(ret)
    else:
        print "Only actions: %s available !" % " | ".join(FUNC_MAPPER.keys())
        sys.exit(1)
