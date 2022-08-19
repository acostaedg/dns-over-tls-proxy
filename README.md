# DNS over TLS Proxy
This is a simple python script to create a DNS over TLS proxy server listening for TCP and UDP.

UDP packets will be converted into TCP by adding a two bytes length field to the UDP data message.

Default connection will be stablished with Cloudflare DNS at 1.0.0.1 at port 853, but you can use custom nameserver passing the environment variable **NAMESERVER** and **NAMESERVER_PORT** during container execution. The python function 
'create_default_context' from the **ssl** library was used to establish connection with the nameserver in a secure encripted manner. The ssl library will load trusted CA certificates from the OS as default, setting the secure 
protocol and ciphers.

The library **socketserver** is used to handle the TCP and UDP requests, and must override the **handle()** method to implement communication to the client and extending the **BaseRequestHandler** class, two different handler classes are needed, one for TCP and antoher for UDP.

Two servers will be instantiated, one for TCP and another for UDP using **ThreadingTCPServer** from **socketserver** library, this way we will be able to handle multiple incoming requests at the same time, each of the servers make use of the corresponding request handler, and to be able to instantiate the two servers, TCP and UDP as processes at the same time the **multiprocessing** library is used in this case. 


## Building the container image
* Enter into the folder */dns-over-tls-proxy* and run the following with docker:

````
docker build -t dns-over-tls-proxy:latest -f Dockerfile .
````


## Running the DNS over TLS Proxy container
* **Default:** default setting will run the DNS over TLS proxy using Cloudflare DNS at 1.0.0.1 and port 853, internally the proxy listens for conenctions on port 30853 which need to be expose in local environment to any available port during container execution:

````
docker run -d --name dns-over-tls-proxy -p <LOCAL_PORT>:30853/udp -p <LOCAL_PORT>:30853/tcp dns-over-tls-proxy:latest
````

- **Example:**

````
docker run -d --name dns-over-tls-proxy -p 8853:30853/udp -p 8853:30853/tcp dns-over-tls-proxy:latest
````

* **Custom DNS:** you can pass the DNS nameserver to use through the enviroment variables **NAMESERVER** and **NAMESERVER_PORT**:

````
docker run -d --name dns-over-tls-proxy -p <LOCAL_PORT>:30853/udp -p <LOCAL_PORT>:30853/tcp -e NAMESERVER=<NAMESERVER_IP> -e NAMESERVER_PORT=<NAMESERVER_PORT> dns-over-tls-proxy:latest
````

- **Example:** let´s say we wnat to use Google's DNS for DNS over TLS use case using Nameserver IP **8.8.8.8** and port **853**

````
docker run -d --name dns-over-tls-proxy -p 8853:30853/udp -p 8853:30853/tcp -e NAMESERVER=8.8.8.8 -e NAMESERVER_PORT=853 dns-over-tls-proxy:latest
````

## Testing the solution

You can use **dig** to test the response from the DNS over TLS proxy in your local enviroment, for example if you exposed the proxy on local port **8853**, run the following command to get the result:

### Only over TCP
````
dig @127.0.0.1 -p 8853 google.com A +tcp

; <<>> DiG 9.10.6 <<>> @127.0.0.1 -p 8853 A google.com +tcp
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 14581
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		137	IN	A	142.250.200.78

;; Query time: 81 msec
;; SERVER: 127.0.0.1#8853(127.0.0.1)
;; WHEN: Fri Aug 19 10:54:38 CEST 2022
;; MSG SIZE  rcvd: 55
````

### Only over UDP  
````
dig @127.0.0.1 -p 8853 google.com A

; <<>> DiG 9.10.6 <<>> @127.0.0.1 -p 8853 google.com A
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 57839
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		33	IN	A	142.250.200.78

;; Query time: 73 msec
;; SERVER: 127.0.0.1#8853(127.0.0.1)
;; WHEN: Fri Aug 19 10:56:23 CEST 2022
;; MSG SIZE  rcvd: 55
````

