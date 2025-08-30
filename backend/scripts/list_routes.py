import os
import sys
# Ensure backend package path is first
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
try:
    import dev_server as ds
    routes = [r.path for r in ds.app.routes]
    admin_routes = [p for p in routes if 'admin' in p]
    print('ADMIN_ROUTES_COUNT:', len(admin_routes))
    for r in admin_routes:
        print(r)
    print('TOTAL_ROUTES:', len(routes))
except Exception as e:
    import traceback
    traceback.print_exc()
    print('ERROR:', e)
