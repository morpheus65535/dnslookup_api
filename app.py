# coding=utf-8

from os import environ
from dns import resolver
from publicsuffix2 import get_sld

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
                    'ip': None,
                    'error': None,
                    'root_domain': True if get_sld(fqdn) == fqdn else False}
        try:
            query_response = resolver.resolve(fqdn, raise_on_no_answer=True)
            response['cname'] = query_response.canonical_name.to_text().strip('.')
            response['ip'] = [x.address for x in query_response]
        except (resolver.NXDOMAIN, resolver.NoNameservers, resolver.NoAnswer) as e:
            response['error'] = repr(e)
        finally:
            return jsonify(response), 200 if not response['error'] else 404


if __name__ == '__main__':
    app.run(host='0.0.0.0')
