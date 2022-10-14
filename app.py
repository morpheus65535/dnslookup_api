from flask import Flask, request, jsonify
import dns.resolver

app = Flask(__name__)


@app.route('dnslookup_api/nslookup', methods=['GET'])
def main():
    args = request.args
    apikey = args.get('apikey')
    fqdn = args.get('fqdn')

    if not apikey:
        return jsonify(error='no apikey provided'), 401
    else:
        if apikey != '1535':
            return jsonify(error='wrong apikey provided'), 401

    if not fqdn:
        return jsonify(error='no fqdn provided'), 400
    else:
        try:
            answers = dns.resolver.resolve(fqdn, 'CNAME')
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            return jsonify({'cname': None})
        for answer in answers:
            return jsonify({'cname': answer.to_text()})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
