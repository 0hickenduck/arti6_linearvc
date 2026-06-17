import json
import os
open("hook_ran.txt", "w").write("ran")
print(json.dumps({"testField": "test"}))
