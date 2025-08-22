import asyncio
import json
import os
import sys

# Ensure backend module is importable
sys.path.insert(0, os.path.dirname(__file__))

import dev_server as ds

async def main():
    # Call health
    try:
        h = await ds.health()
        try:
            h_out = h.dict()
        except Exception:
            h_out = h
    except Exception as e:
        h_out = {"error": str(e)}

    # Call api_status
    try:
        s = await ds.api_status()
        s_out = s
    except Exception as e:
        s_out = {"error": str(e)}

    # Call api_login with demo user
    try:
        lr = ds.LoginRequest(email='free@test.com', password='Free123!')
        l = await ds.api_login(lr)
        try:
            l_out = l.dict()
        except Exception:
            l_out = l
    except Exception as e:
        l_out = {"error": str(e)}

    # Print results as JSON
    print(json.dumps({"health": h_out, "status": s_out, "login": l_out}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    asyncio.run(main())
