# coding=utf-8

import requests

from os import environ
from dns import resolver
from urllib.parse import urlparse

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/dnslookup_api/nslookup', methods=['GET'])
def main():
    args = request.args
    apikey = args.get('apikey')
    fqdn = args.get('fqdn')

    if not apikey:
        return jsonify(error='no apikey provided'), 401
    else:
        if apikey != environ.get('apikey', '1535'):
            return jsonify(error='wrong apikey provided'), 401

    if not fqdn:
        return jsonify(error='no fqdn provided'), 400
    else:
        response = {'cname': None,
                    'from_ptr': False,
                    'redirected': False,
                    'redirect_destination': None,
                    'redirected_by': None,
                    'error': None}
        try:
            answer = resolver.resolve(fqdn, raise_on_no_answer=True)
            if answer.chaining_result.cnames:
                response['cname'] = answer.canonical_name.to_text()
            else:
                try:
                    ip = answer[0].to_text()
                    ptr = resolver.resolve_address(ip)
                    for key, value in ptr.chaining_result.answer.items.items():
                        response['cname'] = key.to_text()
                        response['from_ptr'] = True
                        break
                except Exception as e:
                    print(e)

            req = None
            try:
                req = requests.get(f"https://{fqdn}", allow_redirects=False, timeout=5)
            except requests.exceptions.SSLError:
                try:
                    req = requests.get(f"http://{fqdn}", allow_redirects=False, timeout=5)
                except requests.exceptions.Timeout as e:
                    response['error'] = repr(e)
                except Exception as e:
                    print(e)
            except requests.exceptions.Timeout as e:
                response['error'] = repr(e)
            except Exception as e:
                print(e)
            finally:
                if req and req.is_redirect or req.is_permanent_redirect:
                    response['redirected'] = True
                    if req.headers.get('Location'):
                        response['redirect_destination'] = urlparse(req.headers.get('Location')).hostname
                    response['redirected_by'] = req.headers.get('Server') or 'Akamai'
        except (resolver.NXDOMAIN, resolver.NoNameservers) as e:
            response['error'] = repr(e)
        finally:
            return jsonify(response), 200 if not response['error'] else 404


if __name__ == '__main__':
    app.run(host='0.0.0.0')
