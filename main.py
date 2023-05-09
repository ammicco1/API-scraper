#!/usr/bin/python3

import requests, sys, getopt, json, hashlib

def __usage():
    print("""Usage: python3 main.py [options] hostname
Options: 
    -l (--list=) <filename>, specify a file contains a list of hostname.
    -p (--protocol=) <protocol>, specify the protocol to use, http or https, default is https.
    -o (--output=) <filename>, specify an output file.
    -f (--file) <filename>, specify a file contains a list of API's endpoints.
    -m (--method) <method list>, specify a list of method to use (separate method with comma).
    -v (--verbose), also print 404 endpoints in output file.
    -h (--help), display this help. 
""")

def __parse(filename):
    f = open(filename, "r")
    
    data = json.load(f)

    f.close()

    return data

def __scan(proto, hostname, apis, verbose):
    print()
    out = {}

    for end in apis:
        url = f"{proto}://{hostname}/{end}"

        out[url] = {}

        for met in method: 
            response = requests.request(met, url = url)

            if response.status_code > 199 and response.status_code < 300: 
                if len(response.text) > 40:
                    text = hashlib.md5(response.text.encode()).hexdigest()
                else:
                    text = response.text

                print(f"[ \033[92m OK \033[0m ] - \033[1mUrl\033[0m: \033[96m{url}\033[0m, \
\033[1mmethod\033[0m: \033[91m{met}\033[0m, \
\033[1mstatus\033[0m: \033[93m{response.status_code}\033[0m, \
\033[1mresponse\033[0m: {text}\n")

                r = [response.status_code, text]
                out[url][met] = r
            elif verbose is True:
                if response.status_code != 404:
                    if len(response.text) > 40:
                        text = hashlib.md5(response.text.encode()).hexdigest()
                    else:
                        text = response.text

                    print(f"[ \033[92m OK \033[0m ] - \033[1mUrl\033[0m: \033[96m{url}\033[0m, \
\033[1mmethod\033[0m: \033[91m{met}\033[0m, \
\033[1mstatus\033[0m: \033[93m{response.status_code}\033[0m, \
\033[1mresponse\033[0m: {text}\n")
                
                    r = [response.status_code, text]
                else:
                    r = response.status_code

                out[url][met] = response.status_code

        if not out[url]:
            out.pop(url)
            
    return out

method = ["GET", "POST"]
proto = "https"
hostFile = apiFile = outFile = ""
output = []
verbose = False

try:
    opts, args = getopt.getopt(sys.argv[1:], "l:p:o:f:m:vh", ["list=", "protocol=", "output=", "file=", "method=", "verbose", "help"])
except: 
    __usage()
    exit()

if len(args) > 0:
    hostname = args[0]

for opt, arg in opts:
    if opt in ["-l", "--list="]:
        hostFile = arg
    if opt in ["-p", "--protocol="]:
        proto = arg
    if opt in ["-o", "--output="]:
        outFile = arg
    if opt in ["-f", "--file="]:
        apiFile = arg
    if opt in ["-m", "--method="]:
        mets = arg
        method.clear()

        if "," in mets:
            mets = mets.split(",")

            for m in mets:
                method.append(m)
        else:
            method.append(mets)
    if opt in ["-v", "--verbose"]:
        verbose = True
    if opt in ["-h", "--help"]:
        __usage()
        exit()

apis = __parse(apiFile)

if hostFile != "":
    for hostname in open(hostFile, "r"):
        output.append(__scan(proto, hostname.replace("\n", ""), apis, verbose))
else:
    output.append(__scan(proto, hostname, apis, verbose))

if outFile != "":
    of = open(outFile, "w")

    of.write(json.dumps(output, indent = 2))

    of.close()
