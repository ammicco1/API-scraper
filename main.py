#!/usr/bin/python3

import requests, sys, getopt, json, hashlib

__MAXLEN__ = 60 # if response lenght is higher will be printed its hash 

def __usage(): # function to print an help message
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
    -c (--cookie) <string>, specify a cookie (json format).
    -H (--header) <string>, specify a header in json form to include it in the request.
    -x (--exclude) <status code>, exclude a status code from output.
    -F (--follow), follow redirect.
    -r (--response), print response text in output file instead of hash. In stdout print always the hash.
    -v (--verbose), print all http response code except for 404. Anyway 404 errors are printed in output file.
    -h (--help), display this help. 
""")

def __parse(filename): # function to parse wordlist file into an array
    f = open(filename, "r")
    
    data = json.load(f)

    f.close()

    return data

def __brute_force(apis): # function to combine every word of the wordlist with another one, in this way you can get a double slash endpoint to test with all the combination
    comp_apis = []

    for i in range(len(apis)): 
        comp_apis.append(apis[i])
        
        for j in range(len(apis)):
            if j == i: 
                continue
            else:
                comp_apis.append(f"{apis[i]}/{apis[j]}")

    return comp_apis

def __scan(proto, hostname, apis, verbose, exclude, printRes, body, follow, header, cookie): # function to send request to all the endpoints
    print() # just to leave some space
    out = {} # to create output 
    headers = {} # to store req headers
    cookies ={} # to store req cookies
    r = {} # to store temp output data
    warn = [] # to store warnings

    if header != "": # if pass some headers as argument update the dict 
        headers.update(header)

    if cookies != "":
        cookies.update(cookie)

    for end in apis: # for all the endpoints
        url = f"{proto}://{hostname}/{end}" # create the url with protocol (http or https), hostname and endpoint name

        out[url] = {} # create an entry in the results dict named as the url

        for met in method: # for all the method specified  
            if body[0] == "json" and met == "POST": # if the request is a POST with json payload 
                headers["content-type"] = "application/json" # set the appropriate header
                response = requests.request(met, url = url, json = body[1], allow_redirects = follow, headers = headers, cookies = cookies) # send the request
            elif body[0] == "urlenc" and met == "POST": # if the req is a POST with urlencoded data
                headers["content-type"] = "application/x-www-form-urlencoded" # set the header 
                response = requests.request(met, url = url, data = body[1], allow_redirects = follow, headers = headers, cookies = cookie) # send the request
            else:
                response = requests.request(met, url = url, allow_redirects = follow, headers = headers, cookies = cookie) # if there's no payload send the request

            # if the response code is a 200's family code or verbose is set and code is different from the one to exclude
            if ((response.status_code > 199 and response.status_code < 300) or (verbose is True and response.status_code != 404)) and (response.status_code != int(exclude)):
                if len(response.text) > __MAXLEN__: # if the response text len is higher than the limit
                    text = hashlib.md5(response.text.encode()).hexdigest() # hash the response
                else:
                    text = response.text # else save the plain response

                print(f"[ \033[92m OK \033[0m ] - \033[1mUrl\033[0m: \033[96m{url}\033[0m, \
\033[1mmethod\033[0m: \033[91m{met}\033[0m, \
\033[1mstatus\033[0m: \033[93m{response.status_code}\033[0m, \
\033[1mresponse\033[0m: {text}\n") # print formatted output for the response 

                r["status"] = response.status_code # insert the status code

                if printRes is True: # insert response text 
                    r["response"] = response.text
                else:
                    r["response"] = text

                r["headers"] = dict(response.headers) # insert response headers

                for h in mhead: # check if must have headers isnt set in the response
                    if h not in response.headers:
                        warn.append(f"header {h} not set!") # if isnt set make a warning

                if len(warn) != 0: # if there's some warning add it to the output
                    r["headers"]["header-warnings"] = warn

                if response.cookies != {}: # insert the cookies
                    r["cookies"] = dict(response.cookies)

                warn.clear()

                for c in nhcookie:
                    if c in response.cookies:
                        warn.append(f"found a {c} cookie!")

                if len(warn) != 0: 
                    r["cookies"]["cookie-warnings"] = warn
                
                out[url][met] = r # add r to the output

        if not out[url]:
            out.pop(url)
            
    return out

proto = "https"
hostFile = apiFile = outFile = header = ""

verbose = printRes = follow = False

exclude = 0

cookies = {}

method = ["GET", "POST"]
output = []
body = ["", ""]

mhead = [
    "Content-Security-Policy",
    "X-Frame-Options", 
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy"
]

nhcookie = [
    "id", 
    "sessionId"
]

if sys.argv[1] == "-h":
    start = 1
else:
    start = 2

try:
    opts, args = getopt.getopt(sys.argv[start:], "l:p:o:f:m:j:d:H:c:x:Frvh", ["list=", "protocol=", "output=", "file=", "method=", "json=", "data=", "header=", "cookies=", "exclude=", "follow", "reponse", "verbose", "help"])
except getopt.GetoptError as err:
    print(err) 
    __usage()
    exit()

if len(args) > 0:
    hostname = args[0]

for opt, arg in opts:
    if opt in ["-l", "--list"]:
        hostFile = arg
    if opt in ["-p", "--protocol"]:
        proto = arg
    if opt in ["-o", "--output"]:
        outFile = arg
    if opt in ["-f", "--file"]:
        apiFile = arg
    if opt in ["-m", "--method"]:
        mets = arg
        method.clear()

        if "," in mets:
            mets = mets.split(",")

            for m in mets:
                method.append(m)
        else:
            method.append(mets)
    if opt in ["-j", "--json"]:
        method.pop(0)
        body[0] = "json"
        body[1] = json.loads(arg)  
    if opt in ["-d", "--data"]:
        method.pop(0)
        body[0] = "urlenc"
        body[1] = arg 
    if opt in ["-H", "--header"]:
        header = json.loads(arg)
    if opt in ["-c", "--cookie"]:
        cookies = json.loads(arg)
    if opt in ["-F", "--follow"]:
        follow = True   
    if opt in ["-x", "--exclude"]:  
        exclude = arg
    if opt in ["-r", "--reponse"]:
        printRes = True
    if opt in ["-v", "--verbose"]:
        verbose = True
    if opt in ["-h", "--help"]:
        __usage()
        exit()

command = sys.argv[1]

apis = __parse(apiFile)

if command == "force":
    apis = __brute_force(apis)

if hostFile != "":
    for hostname in open(hostFile, "r"):
        output.append(__scan(proto, hostname.replace("\n", ""), apis, verbose, exclude, printRes, body, follow, header, cookies))
else:
    output.append(__scan(proto, hostname, apis, verbose, exclude, printRes, body, follow, header, cookies))

if outFile != "":
    of = open(outFile, "w")

    of.write(json.dumps(output, indent = 2))

    of.close()
