#!/usr/bin/python3

import requests, sys, getopt, json, hashlib

def __usage():
    print("""Usage: python3 main.py <command> <-f apis-file> [options] <hostname>
Commands:
    - scan, test all the api endpoints in the file.
    - force, combine all the endpoints in the file for create a 2 words endpoints. 
Options: 
    -l (--list) <filename>, specify a file contains a list of hostname.
    -p (--protocol) <protocol>, specify the protocol to use, http or https, default is https.
    -o (--output) <filename>, specify an output file.
    -f (--file) <filename>, specify a file contains a list of API's endpoints.
    -m (--method) <method list>, specify a list of method to use (separate method with comma).
    -j (--json) <string>, specify a json payload for post requests. With this options it send only POST.
    -d (--data) <string>, specify urlencoded data payload for post requests. With this options it send only POST.
    -H (--header) <string>, specify a header in json form to include it in the request.
    -x (--exclude) <status code>, exclude a status code from output.
    -F (--follow), follow redirect.
    -r (--response), print response text in output file instead of hash. In stdout print always the hash.
    -v (--verbose), print all http response code except for 404. Anyway 404 errors are printed in output file.
    -h (--help), display this help. 
""")

def __parse(filename):
    f = open(filename, "r")
    
    data = json.load(f)

    f.close()

    return data

def __brute_force(apis):
    comp_apis = []

    for i in range(len(apis)): 
        comp_apis.append(apis[i])
        
        for j in range(len(apis)):
            if j == i: 
                continue
            else:
                comp_apis.append(f"{apis[i]}/{apis[j]}")

    return comp_apis

def __scan(proto, hostname, apis, verbose, exclude, printRes, body, follow, header):
    print()
    out = {}
    headers = {}

    if header != "":
        headers.update(header)

    for end in apis:
        url = f"{proto}://{hostname}/{end}"

        out[url] = {}

        for met in method: 
            if body[0] == "json" and met == "POST":
                headers["content-type"] = "application/json"
                response = requests.request(met, url = url, json = body[1], allow_redirects = follow, headers = headers)
            elif body[0] == "urlenc" and met == "POST":
                headers["content-type"] = "application/x-www-form-urlencoded"
                response = requests.request(met, url = url, data = body[1], allow_redirects = follow, headers = headers)
            else:
                response = requests.request(met, url = url, allow_redirects = follow, headers = headers)

            if ((response.status_code > 199 and response.status_code < 300) or (verbose is True and response.status_code != 404)) and (response.status_code != int(exclude)): 
                if len(response.text) > 40:
                    text = hashlib.md5(response.text.encode()).hexdigest()
                else:
                    text = response.text

                print(f"[ \033[92m OK \033[0m ] - \033[1mUrl\033[0m: \033[96m{url}\033[0m, \
\033[1mmethod\033[0m: \033[91m{met}\033[0m, \
\033[1mstatus\033[0m: \033[93m{response.status_code}\033[0m, \
\033[1mresponse\033[0m: {text}\n")

                if printRes is True:
                    r = [response.status_code, response.text]
                else:
                    r = [response.status_code, text]
                
                out[url][met] = r
            #elif verbose is True and response.status_code == 404:
            #    out[url][met] =response.status_code

        if not out[url]:
            out.pop(url)
            
    return out

method = ["GET", "POST"]
proto = "https"
hostFile = apiFile = outFile = header = ""
output = []
body = ["", ""]
verbose = printRes = follow = False
exclude = 0

if sys.argv[1] == "-h":
    start = 1
else:
    start = 2

try:
    opts, args = getopt.getopt(sys.argv[start:], "l:p:o:f:m:j:d:H:x:Frvh", ["list=", "protocol=", "output=", "file=", "method=", "json=", "data=", "header=", "exclude=", "follow", "reponse", "verbose", "help"])
except getopt.GetoptError as err:
    print(err) 
    __usage()
    exit()

if len(args) > 0:
    hostname = args[0]

for opt, arg in opts:
    if opt in ["-l", "--list"]:
        hostFile = arg
    elif opt in ["-p", "--protocol"]:
        proto = arg
    elif opt in ["-o", "--output"]:
        outFile = arg
    elif opt in ["-f", "--file"]:
        apiFile = arg
    elif opt in ["-m", "--method"]:
        mets = arg
        method.clear()

        if "," in mets:
            mets = mets.split(",")

            for m in mets:
                method.append(m)
        else:
            method.append(mets)
    elif opt in ["-j", "--json"]:
        method.pop(0)
        body[0] = "json"
        body[1] = json.loads(arg)  
    elif opt in ["-d", "--data"]:
        method.pop(0)
        body[0] = "urlenc"
        body[1] = arg 
    elif opt in ["-H", "--header"]:
        header = json.loads(arg)
    elif opt in ["-F", "--follow"]:
        follow = True   
    elif opt in ["-x", "--exclude"]:  
        exclude = arg
    elif opt in ["-r", "--reponse"]:
        printRes = True
    elif opt in ["-v", "--verbose"]:
        verbose = True
    elif opt in ["-h", "--help"]:
        __usage()
        exit()

command = sys.argv[1]

apis = __parse(apiFile)

if command == "force":
    apis = __brute_force(apis)

if hostFile != "":
    for hostname in open(hostFile, "r"):
        output.append(__scan(proto, hostname.replace("\n", ""), apis, verbose, exclude, printRes, body, follow, header))
else:
    output.append(__scan(proto, hostname, apis, verbose, exclude, printRes, body, follow, header))

if outFile != "":
    of = open(outFile, "w")

    of.write(json.dumps(output, indent = 2))

    of.close()