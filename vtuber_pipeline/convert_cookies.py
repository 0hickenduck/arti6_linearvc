import json
import sys

def convert(json_path, txt_path):
    with open(json_path, 'r') as f:
        cookies = json.load(f)
        
    with open(txt_path, 'w') as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write("# http://curl.haxx.se/rfc/cookie_spec.html\n")
        f.write("# This is a generated file!  Do not edit.\n\n")
        
        for c in cookies:
            domain = c.get('domain', '')
            include_subdomains = 'TRUE' if domain.startswith('.') else 'FALSE'
            path = c.get('path', '/')
            secure = 'TRUE' if c.get('secure', False) else 'FALSE'
            
            # expirationDate can be missing or a float
            expiration = c.get('expirationDate', 0)
            if expiration is not None:
                expiration = int(float(expiration))
            else:
                expiration = 0
                
            name = c.get('name', '')
            value = c.get('value', '')
            
            f.write(f"{domain}\t{include_subdomains}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")

if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2])
