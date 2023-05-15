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
 - x (--exclude) <status code>, exclude a status code from output.
 - F (--follow), follow redirect.
 - r (--response), print response text in output file instead of hash. In stdout print always the hash.
 - v (--verbose), print all http response code except for 404. Anyway 404 errors are printed in output file.
 - h (--help), display help. 