# Simple-Cloudflare-ddns
Very simple cloudflare dynamic dns updater in python.

Currently only works for A and AAAA records.

Api token, zone id and domain reccomended to be hardcoded in main()

Feel free to fork/edit the script to your needs.

Usage:

python3 cloudflareDDNS.py -A 

python3 cloudflareDDNS.py -A -zone="ZONEID"

python3 cloudflareDDNS.py -A -AAAA

python3 cloudflareDDNS.py -AAAA -s # Only run once (-s)

python3 cloudflareDDNS.py -A -t=3600 # sets delay at 1hr (3600 seconds)

etc...
