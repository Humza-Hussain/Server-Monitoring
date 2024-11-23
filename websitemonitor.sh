#!/bin/bash
usr_id="3"
websites=("https://antidht.com" "https://biotinconditioner.com" "https://freshrichie.com" "https://nft20.com" "https://minoxidilspray.com" "https://regenepure.ae" "https://regenepure.ca" "https://regenepure.com" "https://regenepure.co.uk" "https://regenepure.in" "https://regenepurewholesale.com" "https://regrowthclub.com" "https://salonceuticals.org" "https://regrowth.com")
endpoint="http://127.0.0.1:5000/website-down"
lst_website=""
for website in "${websites[@]}"; do
    status=$(curl -o /dev/null -s -w "%{http_code}\n" $website)
    if [[ $status != 301 && $status != 302 && $status != 200 ]]; then
    lst_website+="${website},"
fi
done
curl -X POST -H "Content-Type: application/json" -d "{\"website\": \"$lst_website\", \"status\": \"$status\",\"usrid\": \"$usr_id\"}" "$endpoint"