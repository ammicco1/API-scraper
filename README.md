# Simple python script to test a list of API 

This script is usefull to test a list of API on a domain. An example is:
``` bash
    python3 main.py scan -f api_list.json localhost:3000
```

As you can see the script take in input 2 essential arguments: 
 - A list of API endpoints from a json file that contains an array: 
    ``` json
        [
            "testapi/v1/test",
            "post/testdata",
            "testAPI"
        ]
    ```
 - A domain name

The output is like: 
``` bash
    [  OK  ] - Url: http://localhost:3000/testapi/v1/test, method: GET, status: 200, response: 25762da4fef7ed704a8746ac7a0d37ec
```

So, by default it contains all the endpoints returned a 200 status code with: 
 - Complete url.
 - Method. 
 - Status code.
 - An hash of the response so you can easily compare it.

You can include some headers to check if they're not set, or some cookies to check if they're set. Include that in these files: 
 - headers.json, by default check: 
    - Content-Security-Policy
    - X-Frame-Options
    - X-Content-Type-Options
    - Referrer-Policy
    - Permissions-Policy
 - cookies.json, by default it includes: 
    - sessionId cookie
    - id cookie

The output file generated with this command:
``` bash
    python3 main.py force -f api.json -o output.json -m GET,POST,PUT -p http -F localhost:3000
```

is: 
``` json
    [{
        "used command": "main.py force -f api.json -o output.json -m GET,POST,PUT -p http -F localhost:3000 ",
        "http://localhost:3000/test/test-end": {
            "GET": {
                "status": 200,
                "response": "/",
                "headers": {
                  "X-Powered-By": "Express",
                  "X-Frame-Options": "SAMEORIGIN",
                  "Permissions-Policy": "geolocation=(self hostname), microphone=()",
                  "Set-Cookie": "sessionId=ugvdcbhin3892duibas!23; Path=/",
                  "Content-Type": "text/html; charset=utf-8",
                  "Content-Length": "1",
                  "ETag": "W/\"1-QgmbSvAh5T/Y/U4FbCVo18Lj/6g\"",
                  "Date": "Thu, 08 Jun 2023 07:27:16 GMT",
                  "Connection": "keep-alive",
                  "Keep-Alive": "timeout=5",
                  "header-warnings": [
                    "header Content-Security-Policy not set!",
                    "header X-Content-Type-Options not set!",
                    "header Referrer-Policy not set!",
                  ]
                },
                "cookies": {
                  "sessionId": "ugvdcbhin3892duibas!23",
                  "cookie-warnings": [
                    "found a sessionId cookie!"
                  ]
                }
            } 
        },
    ...
    }]
```

### Commands 
The possible commands are: 
 - scan, test all the api endpoints in the file.
 - force, combine all the endpoints in the file for create a 2 words endpoints and test it. For example: 
   - file endpoints: 
     - test
     - api 

    - result endpoints:
      - test
      - test/api
      - api
      - api/test 

Obviusly force command takes a lot of time

### Options
Some options can help to use the script: 
 - l (--list) <filename>, specify a file contains a list of hostname.
 - p (--protocol) <protocol>, specify the protocol to use, http or https, default is https.
 - o (--output) <filename>, specify an output file.
 - f (--file) <filename>, specify a file contains a list of API's endpoints.
 - m (--method) <method list>, specify a list of method to use (separate method with comma).
 - j (--json) <string>, specify a json payload for post requests. With this options it send only POST.
 - d (--data) <string>, specify urlencoded data payload for post requests. With this options it send only POST.
 - H (--header) <string>, specify a header in json form to include it in the request.
 - c (--cookie) <string>, specify a cokie in json form.
 - x (--exclude) <status code>, exclude a status code from output.
 - F (--follow), follow redirect.
 - r (--response), print response text in output file instead of hash. In stdout print always the hash.
 - v (--verbose), print all http response code except for 404. Anyway 404 errors are printed in output file.
 - h (--help), display help. 