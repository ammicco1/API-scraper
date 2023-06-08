#!/usr/bin/python3

import requests, sys, getopt, json, hashlib

__MAXLEN__ = 120 # if response lenght is higher will be printed its hash 

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

def __scan(proto, method, hostname, apis, verbose, exclude, printRes, body, follow, header, cookie): # function to send request to all the endpoints
    out = {} # to create output 
    headers = {} # to store req headers
    cookies ={} # to store req cookies

    out["used command"] = cmd

    if header != "": # if pass some headers or cookie as argument update the dict 
        headers.update(header)

    if cookies != "":
        cookies.update(cookie)

    print() # just to leave some space

    for end in apis: # for all the endpoints
        url = f"{proto}://{hostname}/{end}" # create the url with protocol (http or https), hostname and endpoint name

        out[url] = {} # create an entry in the results dict named as the url

        for met in method: # for all the method specified 
            r = {} # to store temp output data 
            hwarn = [] # to store warnings
            cwarn = []
            
            if met == "POST" and (body[0] == "json" or body[0] == "urlenc"):
                if body[0] == "json":
                    headers["content-type"] = "application/json" # set the appropriate header
                    response = requests.request(met, url = url, json = body[1], allow_redirects = follow, headers = headers, cookies = cookies) # send the request
                elif body[0] == "urlenc": 
                    headers["content-type"] = "application/x-www-form-urlencoded" # set the header 
                    response = requests.request(met, url = url, data = body[1], allow_redirects = follow, headers = headers, cookies = cookie) # send the request
            else:
                response = requests.request(met, url = url, allow_redirects = follow, headers = headers, cookies = cookie) # if there's no payload send the request

            # if the response code is a 200's family code or verbose is set and code is different from the one to exclude
            if ((response.status_code > 199 and response.status_code < 300) or (verbose is True and response.status_code != 404)) and (response.status_code != int(exclude)):
                if len(response.text) > __MAXLEN__ and printRes == False: # if the response text len is higher than the limit
                    text = hashlib.md5(response.text.encode()).hexdigest() # hash the response
                else:
                    text = response.text # else save the plain response

                # print formatted output for the response 
                print(f"[ \033[92m OK \033[0m ] - \033[1mUrl\033[0m: \033[96m{url}\033[0m, \033[1mmethod\033[0m: \033[91m{met}\033[0m, \033[1mstatus\033[0m: \033[93m{response.status_code}\033[0m, \033[1mresponse\033[0m: {text}\n")

                r["status"] = response.status_code # insert the status code
                r["response"] = text # insert the response text
                r["headers"] = dict(response.headers) # insert response headers

                for h in __MHEAD__: # check if must have headers isnt set in the response
                    if h not in response.headers:
                        hwarn.append(f"header {h} not set!") # if isnt set make a warning

                if len(hwarn) != 0: # if there's some warning add it to the output
                    r["headers"]["header-warnings"] = hwarn

                if response.cookies != {}: # insert the cookies
                    r["cookies"] = dict(response.cookies)

                for c in __NHCOOKIE__: # check if there's some interesting cookies in the response
                    if c in response.cookies:
                        cwarn.append(f"found a {c} cookie!")

                if len(cwarn) != 0: 
                    r["cookies"]["cookie-warnings"] = cwarn
                
                out[url][met] = r # add r to the output

        if not out[url]: # if the endpoint doesnt responde, not include in the output
            out.pop(url)
            
    return out

def __main(): # main function
    proto = "https" # default protocol is https
    hostFile = apiFile = outFile = header = "" # some stuff
    global cmd

    cmd = ""
    
    verbose = printRes = follow = False

    exclude = 0

    cookies = {}

    method = ["GET", "POST"] # default methods are GET and POST
    output = []
    body = ["", ""]

    if ("-h" in sys.argv or "--help" in sys.argv) or ("-f" not in sys.argv and "--file" not in sys.argv) or (sys.argv[1] != "scan" and sys.argv[1] != "force"): # if -h is in the args or
        __usage()                                                                                                                                               # if -f not in arsg or
        exit()   
        
    for cmd_parts in sys.argv:
        cmd += f"{cmd_parts} "                                                                                                                                               # if argv[1] isnt the command, display help

    # parse arguments
    try:
        opts, args = getopt.getopt(sys.argv[2:], 
        "l:p:o:f:m:j:d:H:c:x:Frvh", 
        ["list=", "protocol=", "output=", "file=", "method=", "json=", "data=", "header=", "cookies=", "exclude=", "follow", "reponse", "verbose", "help"])
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
            method = ["POST"]
            body[0] = "json"
            body[1] = json.loads(arg)  
        elif opt in ["-d", "--data"]:
            method = ["POST"]
            body[0] = "urlenc"
            body[1] = arg 
        elif opt in ["-H", "--header"]:
            header = json.loads(arg)
        elif opt in ["-c", "--cookie"]:
            cookies = json.loads(arg)
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

    apis = __parse(apiFile) # get apis list
    global __MHEAD__  # get headers list
    global __NHCOOKIE__ # get cookies list

    __MHEAD__ = __parse("headers.json")
    __NHCOOKIE__ = __parse("cookies.json")

    if command == "force": # if the command is force, create the endpoints
        apis = __brute_force(apis)

    if hostFile != "": # if there's a hostnames file, scan all of them
        for hostname in open(hostFile, "r"):
            output.append(__scan(proto, method, hostname.replace("\n", ""), apis, verbose, exclude, printRes, body, follow, header, cookies))
    else: # else scan the only one
        output.append(__scan(proto, method, hostname, apis, verbose, exclude, printRes, body, follow, header, cookies))

    if outFile != "": # if indicate an output file write the output on this
        of = open(outFile, "w")
        
        of.write(json.dumps(output, indent = 2))

        of.close()

__main() # start