#!/usr/bin/env python3

import requests
import sys
import time

help = """
-v = Verbose output
-A = update IPv4 records
-AAAA = update IPv6 records
-ZONE=<zone_id> = Cloudflare zone ID
-d4=<ip> = IPv4 record destination
-d6=<ip> = IPv6 record destination
-t=<seconds> = loop delay in seconds
-s = run once (no loop)
"""

successStatusCodes = [200]

class cloudflareClient:
    def __init__(self, apiToken):
        self._apiToken = apiToken
        url = "https://api.cloudflare.com/client/v4/user/tokens/verify"
        headers = {"Authorization": f"Bearer {apiToken}"}
        response = requests.get(url, headers=headers)
        self._authResponse = response

    def getRecordId(self, zone, domain, record_type):
        url = f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records"
        headers = {"Authorization": f"Bearer {self._apiToken}"}
        response = requests.get(url, headers=headers).json()
        for rec in response["result"]:
            if rec["name"] == domain and rec["type"] == record_type:
                return rec["id"]
        return None

    def updateDnsRecord(self, zone, record_type, dest, domain, proxied=False, ttl=1):
        record_id = self.getRecordId(zone, domain, record_type)
        if not record_id:
            print(f"Record of type {record_type} not found for {domain}")
            return None
        url = f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records/{record_id}"
        headers = {
            "Authorization": f"Bearer {self._apiToken}",
            "Content-Type": "application/json"
        }
        data = {
            "type": record_type,
            "name": domain,
            "content": dest,
            "ttl": ttl,
            "proxied": proxied
        }
        return requests.put(url, headers=headers, json=data)
    
    def getDnsRecordValue(self, zone, domain, record_type):
        url = f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records"
        headers = {"Authorization": f"Bearer {self._apiToken}"}
        response = requests.get(url, headers=headers).json()
        
        for rec in response["result"]:
            if rec["name"] == domain and rec["type"] == record_type:
                return rec["content"]
        
        return ""

def getPublicIpIpv4():
    ip = requests.get("https://1.1.1.1/cdn-cgi/trace").text
    for line in ip.splitlines():
        if line.startswith("ip="):
            return line.split("=")[1]

def getPublicIpIpv6():
    ip = requests.get("https://[2606:4700:4700::1111]/cdn-cgi/trace").text
    for line in ip.splitlines():
        if line.startswith("ip="):
            return line.split("=")[1]
        
def main(lasts,delay=120): # Default 2 minutes
    apiToken = "YourApiToken"  # KEEP SECRET
    a = False
    aaaa = False
    dest4 = ""
    dest6 = ""
    zone = "YourCloudFlareZoneId"
    domain = "YourDomain.com"
    checkIfLast = True
    loop = True

    # Arguments parsing
    verbose = "-v" in sys.argv or "-V" in sys.argv

    for arg in sys.argv:
        if "-a" in arg.lower() and "-aaaa" not in arg.lower():
            a = True
        if "-aaaa" in arg.lower():
            aaaa = True
        if "-s" in arg.lower():
            loop = False
        if "-zone" in arg.lower():
            zone = arg.split("=")[1]
        if "-d4" in arg.lower():
            dest4 = arg.split("=")[1]
        if "-d6" in arg.lower():
            dest6 = arg.split("=")[1]
        if "-t" in arg.lower():
            delay = float(arg.split("=")[1])

    if a:
        if dest4 == "":
            dest4 = getPublicIpIpv4()
    if aaaa:
        if dest6 == "":
            dest6 = getPublicIpIpv6()

    if (checkIfLast == True and (dest6 not in lasts or dest4 not in lasts)) or checkIfLast == False:
        client = cloudflareClient(apiToken)
    else:
        if verbose:
            print("No records changed... Returning.")
        if loop:
            time.sleep(delay)
        return [dest4,dest6], loop

    if client._authResponse.status_code in successStatusCodes:
        print("Authentication successful!")
    else:
        print(f"AUTHENTICATION FAILED! (Cloudflare responded with code: {client._authResponse.status_code})")
        if verbose:
            print(client._authResponse.text)
        exit(1)

    if a:
        if checkIfLast == True and dest4 not in lasts:
            resp = client.updateDnsRecord(zone, "A", dest4, domain)
            if resp and resp.status_code in successStatusCodes:
                print(f"A record updated to {dest4}")
            else:
                print("FAILED UPDATING A RECORD!")
            if verbose and resp:
                print(resp.text)
        elif verbose:
            print("A record not changed... continuing.")

    if aaaa:
        if checkIfLast == True and dest6 not in lasts:
            resp = client.updateDnsRecord(zone, "AAAA", dest6, domain)
            if resp and resp.status_code in successStatusCodes:
                print(f"AAAA record updated to {dest6}")
            else:
                print("FAILED UPDATING AAAA RECORD!")
            if verbose and resp:
                print(resp.text)
        elif verbose:
            print("AAAA record not changed... continuing.")

    if loop:
        time.sleep(delay)
    return [dest4,dest6], loop

lasts = []
loop = True
if __name__ == "__main__":
    while loop:
        try:
            lasts,loop = main(lasts)
        except Exception as ex:
            print(str(ex))
            time.sleep(30)
    


    

    