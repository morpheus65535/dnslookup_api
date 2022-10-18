# coding=utf-8

from os import environ
import dns.resolver

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
        try:
            answer = dns.resolver.resolve(fqdn, raise_on_no_answer=True)
            canonical_name = answer.canonical_name
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers) as e:
            return jsonify({'cname': None, 'error': repr(e)}), 404
        else:
            return jsonify({'cname': canonical_name.to_text()}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
