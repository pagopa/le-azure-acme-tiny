#!/usr/bin/env python3
# Copyright Daniel Roesler, under MIT license, see LICENSE at github.com/diafygi/acme-tiny

import argparse
import base64
import hashlib
import json
import logging
import os
import re
import sys
import textwrap
import time
import urllib.request

import azure.identity
import azure.mgmt.dns
import cryptography
import jwcrypto.jwk

DEFAULT_DIRECTORY_URL = "https://acme-v02.api.letsencrypt.org/directory"
DEFAULT_DNS_TTL_SEC = 300

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.INFO)


def azure_dns_operation(subscription, resource_group, zone, domain, value, operation):

    log = LOGGER

    # helper function - get a DNS API client
    def _get_dns_client(subscription):
        identity = azure.identity.ClientSecretCredential(
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
            tenant_id=os.environ["AZURE_TENANT_ID"]
        )
        return azure.mgmt.dns.DnsManagementClient(identity, subscription)

    # helper function - remove zone name from domain string
    def _get_name(domain, zone):
        if domain.endswith(".{}".format(zone)):
            domain = domain[:-len(".{}".format(zone))]
        return "_acme-challenge.{}".format(domain)

    client = _get_dns_client(subscription)
    log.info("Azure DNS client initialized")

    # get the domain without the zone name
    name = _get_name(domain, zone)

    if operation == "update":
        log.info("Updating TXT record on %s in %s zone with value %s", name, zone, value)
        client.record_sets.create_or_update(
            resource_group,
            zone,
            name,
            "TXT",
            {
                "ttl": DEFAULT_DNS_TTL_SEC,
                "txt_records": [{"value": [value]}]
            }
        )

        log.info("TXT record updated!")
    elif operation == "delete":

        log.info("Deleting TXT record on %s in %s zone", name, zone)
        client.record_sets.delete(
            resource_group,
            zone,
            _get_name(domain, zone),
            "TXT"
        )
        log.info("TXT record deleted!")
    else:
        raise ValueError("Unknown DNS operation: {}".format(operation))


def get_crt(private_key, regr, csr, directory_url, out):

    log = LOGGER
    directory, alg = None, None  # global variables

    # helper function - base64 encode for jose spec
    def _b64(b):
        return base64.urlsafe_b64encode(b).decode('utf8').replace("=", "")

    # helper function - make request and automatically parse json response
    def _do_request(url, data=None, err_msg="Error", depth=0):
        req = urllib.request.Request(
            url, data=data, headers={
                "Content-Type": "application/jose+json", "User-Agent": "acme-tiny"}
        )
        if req.type != "https":
            raise ValueError("{}:\nUrl: {}".format("Disallowed schema", url))
        try:
            resp = urllib.request.urlopen(req)
            resp_data, code, headers = resp.read().decode(
                "utf8"), resp.getcode(), resp.headers
        except IOError as e:
            resp_data = e.read().decode("utf8") if hasattr(e, "read") else str(e)
            code, headers = getattr(e, "code", None), {}
        try:
            resp_data = json.loads(resp_data)  # try to parse json results
        except ValueError:
            pass  # ignore json parsing errors
        if depth < 100 and code == 400 and resp_data['type'] == "urn:ietf:params:acme:error:badNonce":
            raise IndexError(resp_data)  # allow 100 retrys for bad nonces
        if code not in [200, 201, 204]:
            raise ValueError("{}:\nUrl: {}\nData: {}\nResponse Code: {}\nResponse: {}".format(
                err_msg, url, data, code, resp_data))
        return resp_data, code, headers

    # helper function - sign with cryptography module
    def _sign(private_key, alg, payload):
        if alg == "RS256":
            return private_key.sign(
                payload,
                cryptography.hazmat.primitives.asymmetric.padding.PKCS1v15(),
                cryptography.hazmat.primitives.hashes.SHA256())  # RS256
        return private_key.sign(
            payload,
            cryptography.hazmat.primitives.asymmetric.ec.ECDSA(
                cryptography.hazmat.primitives.hashes.SHA256())
        )  # ES256

    # helper function - make signed requests
    def _send_signed_request(url, payload, err_msg, depth=0):
        payload64 = "" if payload is None else _b64(
            json.dumps(payload).encode('utf8'))
        new_nonce = _do_request(directory['newNonce'])[2]['Replay-Nonce']
        protected = {"url": url, "alg": alg, "nonce": new_nonce, "kid": kid}
        protected64 = _b64(json.dumps(protected).encode('utf8'))
        signature64 = _b64(_sign(private_key, alg, "{}.{}".format(
            protected64, payload64).encode("utf-8")))
        data = json.dumps(
            {"protected": protected64, "payload": payload64, "signature": signature64})
        try:
            return _do_request(url, data=data.encode('utf8'), err_msg=err_msg, depth=depth)
        except IndexError:  # retry bad nonces (they raise IndexError)
            return _send_signed_request(url, payload, err_msg, depth=(depth + 1))

    # helper function - poll until complete
    def _poll_until_not(url, pending_statuses, err_msg):
        result, t0 = None, time.time()
        while result is None or result['status'] in pending_statuses:
            if (time.time() - t0 > 3600):  # 1 hour timeout
                raise ValueError("Polling timeout")
            time.sleep(0 if result is None else 2)
            result, _, _ = _send_signed_request(url, None, err_msg)
        return result

    # read private_key.json file
    log.info("Parsing the --private-key file...")
    with open(private_key, "r") as f:
        jwk = jwcrypto.jwk.JWK.from_json(f.read())
    thumbprint = jwk.thumbprint()
    log.info("JWK thumbprint: %s", thumbprint)
    private_key = cryptography.hazmat.primitives.serialization.load_pem_private_key(
        jwk.export_to_pem(private_key=True, password=None), password=None)
    log.info("Private key loaded")

    if jwk.key_type == "RSA":
        alg = "RS256"
    elif jwk.key_type == "EC":
        alg = "ES256"
    else:
        raise ValueError("Unknown JWK key_type: {}".format(jwk.key_type))

    # read regr.json file
    log.info("Parsing the --regr file...")
    with open(regr, "r") as f:
        kid = json.loads(f.read())["uri"]
    log.info("Account kid: %s", kid)

    # read the csr file
    log.info("Parsing the --csr file...")
    with open(csr, "rb") as f:
        csr_raw = f.read()
    csr_der = cryptography.x509.load_der_x509_csr(csr_raw)

    # read the CN and SAN fields from the CSR - ASSUMPTION: just one field for CN -> [0]
    common_name = [csr_der.subject.get_attributes_for_oid(
        cryptography.x509.OID_COMMON_NAME)[0].value.strip()]
    log.info("CSR CN: %s", common_name)
    try:
        subject_alternative_names = list(map(
            lambda x: x.value,
            csr_der.extensions.get_extension_for_oid(
                cryptography.x509.OID_SUBJECT_ALTERNATIVE_NAME).value
        ))
    except cryptography.x509.extensions.ExtensionNotFound:
        subject_alternative_names = []
    log.info("CSR SAN: %s", subject_alternative_names)
    # get the union of this set
    domains = list(set().union(subject_alternative_names, common_name))
    log.info("Domains to validate: %s", ", ".join(domains))

    # sanity check: dns zone domain should be a suffix of domain
    # read zone from env variable, it has been checked earlier so it must exist
    zone = os.environ["AZURE_DNS_ZONE"]
    valid_domains = list(filter(lambda d: d.endswith(zone), domains))
    if len(valid_domains) != len(domains):
        raise ValueError(
            "Domains do not belong to {} DNS zone: {}".format(
                zone,
                list(set(domains) - set(valid_domains))
            ),
        )

    log.info("Now using ACMEv2, getting the directory...")
    directory, _, _ = _do_request(
        directory_url, err_msg="Error getting directory")
    log.info("Directory found!")

    # create a new order
    log.info("Creating a new order...")
    order_payload = {"identifiers": [
        {"type": "dns", "value": d} for d in domains]}
    order, _, order_headers = _send_signed_request(
        directory['newOrder'], order_payload, "Error creating new order")
    log.info("Order created!")

    # get the authorizations that need to be completed
    for auth_url in order['authorizations']:
        authorization, _, _ = _send_signed_request(
            auth_url, None, "Error getting challenges")
        domain = authorization['identifier']['value']
        log.info("Verifying %s...", domain)

        # find the http-01 challenge and write the challenge file
        challenge = [c for c in authorization['challenges']
                     if c['type'] == "dns-01"][0]
        token = re.sub(r"[^A-Za-z0-9_\-]", "_", challenge['token'])
        txt_record_value = _b64(hashlib.sha256(
            "{}.{}".format(token, thumbprint).encode("utf-8")).digest())
        log.info("A TXT record on _acme-challenge.%s must be set to %s",
                 domain, txt_record_value)

        # those env variables must exist, as they have been checked earlier at startup
        subscription = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["AZURE_DNS_ZONE_RESOURCE_GROUP"]

        # modify DNS record
        azure_dns_operation(subscription, resource_group,
                            zone, domain, txt_record_value, "update")

        # check until the challenge is done
        _send_signed_request(
            challenge['url'], {}, "Error submitting challenges: {}".format(domain))
        authorization = _poll_until_not(
            auth_url, ["pending"], "Error checking challenge status for {}".format(domain))
        if authorization['status'] != "valid":
            raise ValueError(
                "Challenge did not pass for {}: {}".format(domain, authorization))
        log.info("%s verified!", domain)

    # finalize the order with the csr
    log.info("Asking to sign the certificate...")
    _send_signed_request(order['finalize'], {
                         "csr": _b64(csr_raw)}, "Error finalizing order")

    # poll the order to monitor when it's done
    order = _poll_until_not(order_headers['Location'], [
                            "pending", "processing"], "Error checking order status")
    if order['status'] != "valid":
        raise ValueError("Order failed: {}".format(order))
    log.info("Order is valid")

    # download the certificate
    certificate_pem, _, _ = _send_signed_request(
        order['certificate'], None, "Certificate download failed")
    log.info("Certificate signed!")

    with open(out, "wb") as f:
        f.write(bytes(certificate_pem, "utf-8"))
    log.info("Certificate bundle saved to %s", out)

    # attempt to cleanup DNS records
    for domain in domains:
        try:
            azure_dns_operation(subscription, resource_group,
                                zone, domain, txt_record_value, "delete")
        except Exception as ex:
            log.info("Exception \"%s\" when cleaning up TXT record on %s, skipping this record", str(ex))
            continue  # ignore failures here


def main(argv=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
            This script automates the process of getting a signed TLS certificate from Let's Encrypt using
            the ACME protocol. It is intented to be run in a Azure DevOps pipeline and have access to your private
            account key, so PLEASE READ THROUGH IT! It's only ~300 lines, so it won't take long.

            Example Usage:
            python3 acme_tiny.py --private-key ./private_key.json --regr ./regr.json --csr ./domain.csr.der --out signed_chain.crt
            """)
    )
    parser.add_argument("--private-key", default="private_key.json",
                        help="Path to your Let's Encrypt account private key")
    parser.add_argument("--regr", default="regr.json",
                        help="Path to your Let's Encrypt account registration info")
    parser.add_argument("--csr", default="csr.der",
                        help="Path to your certificate signing request")
    parser.add_argument("--quiet", action="store_const",
                        const=logging.ERROR, help="Suppress output except for errors")
    parser.add_argument("--directory-url", default=DEFAULT_DIRECTORY_URL,
                        help="Certificate authority directory url, default is Let's Encrypt")
    parser.add_argument("--out", default="certificate_chain.pem",
                        help="Destination path of the certificate")

    args = parser.parse_args(argv)
    LOGGER.setLevel(args.quiet or LOGGER.level)

    # check that all needed env variables are set, bail out early raising an exception otherwise
    os.environ["AZURE_SUBSCRIPTION_ID"]
    os.environ["AZURE_DNS_ZONE_RESOURCE_GROUP"]
    os.environ["AZURE_DNS_ZONE"]
    os.environ["AZURE_CLIENT_ID"]
    os.environ["AZURE_CLIENT_SECRET"]
    os.environ["AZURE_TENANT_ID"]

    # main function
    get_crt(args.private_key, args.regr, args.csr,
            args.directory_url, args.out)


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
