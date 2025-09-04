#!/usr/bin/env python3
"""Simple configurable aiohttp reverse proxy for /api -> backend.

Usage: python scripts/server_proxy_switch.py --backend-port 8001 --listen-port 8000
"""
import argparse
import asyncio
from aiohttp import web, ClientSession


async def proxy_handle(request, backend):
    # forward the incoming request to backend preserving method, path, qs and body
    url = f"{backend}{request.rel_url.path_qs}"
    method = request.method
    headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
    data = await request.read()
    async with ClientSession() as session:
        async with session.request(method, url, headers=headers, data=data, allow_redirects=False) as resp:
            body = await resp.read()
            hdrs = {k: v for k, v in resp.headers.items() if k.lower() not in ('transfer-encoding', 'connection')}
            return web.Response(body=body, status=resp.status, headers=hdrs)


def create_app(backend_url: str):
    app = web.Application()
    # proxy any path starting with /api
    async def handler(request):
        return await proxy_handle(request, backend_url)

    app.router.add_route('*', '/api{tail:.*}', handler)
    return app


def main():
    parser = argparse.ArgumentParser(description='Run a simple proxy forwarding /api to backend')
    parser.add_argument('--backend-host', default='127.0.0.1', help='Backend host (default 127.0.0.1)')
    parser.add_argument('--backend-port', type=int, default=8001, help='Backend port (default 8001)')
    parser.add_argument('--listen-host', default='127.0.0.1', help='Proxy listen host (default 127.0.0.1)')
    parser.add_argument('--listen-port', type=int, default=8000, help='Proxy listen port (default 8000)')
    args = parser.parse_args()

    backend_url = f"http://{args.backend_host}:{args.backend_port}"
    app = create_app(backend_url)
    web.run_app(app, host=args.listen_host, port=args.listen_port)


if __name__ == '__main__':
    main()
