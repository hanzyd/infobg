#!/opt/homebrew/bin/bash

file_list=$(find . -name "*.json")

for file in $file_list; do 
    jq '.' --indent 4 "$file" > tmp
    mv tmp "$file"
done