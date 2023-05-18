import re
import smtplib
import logging
import socket

try:
    import DNS
    ServerError = DNS.ServerError
    DNS.DiscoverNameServers()
except (ImportError, AttributeError):
    DNS = None

    class ServerError(Exception):
        pass

WSP = r'[\s]'
CRLF = r'(?:\r\n)'
NO_WS_CTL = r'\x01-\x08\x0b\x0c\x0f-\x1f\x7f'
QUOTED_PAIR = r'(?:\\.)'
FWS = r'(?:(?:' + WSP + r'*' + CRLF + r')?' + \
      WSP + r'+)'
CTEXT = r'[' + NO_WS_CTL + \
        r'\x21-\x27\x2a-\x5b\x5d-\x7e]'
CCONTENT = r'(?:' + CTEXT + r'|' + \
           QUOTED_PAIR + r')'
# as well, but that would be circular.)
COMMENT = r'\((?:' + FWS + r'?' + CCONTENT + \
          r')*' + FWS + r'?\)'
CFWS = r'(?:' + FWS + r'?' + COMMENT + ')*(?:' + \
       FWS + '?' + COMMENT + '|' + FWS + ')'
ATEXT = r'[\w!#$%&\'\*\+\-/=\?\^`\{\|\}~]'
ATOM = CFWS + r'?' + ATEXT + r'+' + CFWS + r'?'
DOT_ATOM_TEXT = ATEXT + r'+(?:\.' + ATEXT + r'+)*'
DOT_ATOM = CFWS + r'?' + DOT_ATOM_TEXT + CFWS + r'?'
QTEXT = r'[' + NO_WS_CTL + \
        r'\x21\x23-\x5b\x5d-\x7e]'
QCONTENT = r'(?:' + QTEXT + r'|' + \
           QUOTED_PAIR + r')'
QUOTED_STRING = CFWS + r'?' + r'"(?:' + FWS + \
                r'?' + QCONTENT + r')*' + FWS + \
                r'?' + r'"' + CFWS + r'?'
LOCAL_PART = r'(?:' + DOT_ATOM + r'|' + \
             QUOTED_STRING + r')'
DTEXT = r'[' + NO_WS_CTL + r'\x21-\x5a\x5e-\x7e]'
DCONTENT = r'(?:' + DTEXT + r'|' + \
           QUOTED_PAIR + r')'
DOMAIN_LITERAL = CFWS + r'?' + r'\[' + \
                 r'(?:' + FWS + r'?' + DCONTENT + \
                 r')*' + FWS + r'?\]' + CFWS + r'?'
DOMAIN = r'(?:' + DOT_ATOM + r'|' + \
         DOMAIN_LITERAL + r')'
ADDR_SPEC = LOCAL_PART + r'@' + DOMAIN

VALID_ADDRESS_REGEXP = '^' + ADDR_SPEC + '$'

MX_DNS_CACHE = {}
MX_CHECK_CACHE = {}

email = 'kperez@autotropical.com'

class EmailDNSValidator(object):

    def __init__(self, email: str):
        self.email = email
        self._smtp = smtplib.SMTP(timeout=10)

        self._GENERIC_MESSAGE = "Try with email_protected=False"

    def _get_mx_ip(self, hostname):
        if hostname not in MX_DNS_CACHE:
            try:
                MX_DNS_CACHE[hostname] = DNS.mxlookup(hostname)
            except ServerError as e:
                if e.rcode == 3 or e.rcode == 2:
                    MX_DNS_CACHE[hostname] = None
                else:
                    raise

        return MX_DNS_CACHE[hostname]

    def validate_email(self, email_protected=True, verify=False):
        hostname = self._get_hostname()
        domain = self._get_domain(hostname)
        mx_hosts = self._get_mx_ip(hostname)

        if mx_hosts is None:
            return False

        for current_host in mx_hosts:
            try:
                if not verify and current_host[1] in MX_CHECK_CACHE:
                    return MX_CHECK_CACHE[current_host[1]]

                if self._domain_exists(email_protected=email_protected, domain=domain, current_host=current_host):
                    return True

                self._connect_smtp(current_host)
                MX_CHECK_CACHE[current_host[1]] = True

                if not verify:
                    try:
                        self._disconnect_smtp()
                    except smtplib.SMTPServerDisconnected:
                        pass
                    return True

                status, _ = self._smtp.helo()
                if status != 250:
                    self._disconnect_smtp()
                    print(f'{current_host[1]} answer: {status} - {_}. {self._GENERIC_MESSAGE}')
                    continue
                self._smtp.mail('')

                status, _ = self._smtp.rcpt(self.email)
                if status == 250:
                    self._disconnect_smtp()
                    return True
                print(f'{current_host[1]} answer: {status} - {_}. {self._GENERIC_MESSAGE}')
                self._disconnect_smtp()

                return False
            except smtplib.SMTPServerDisconnected:
                if email_protected and domain in current_host[1]:
                    return True
                print(f'{current_host[1]} disconected. {self._GENERIC_MESSAGE}')
                return False
            except smtplib.SMTPConnectError:
                if email_protected and domain in current_host[1]:
                    return True
                print(f'Unable to connect to {current_host[1]}. Try with email_protected=False')
                return False

    def _get_hostname(self):
        return self.email[self.email.find('@') + 1:]

    def _get_domain(self, hostname):
        return hostname.split('.')[0]

    def _domain_exists(self, **kwargs):
        return kwargs['email_protected'] and kwargs['domain'] in kwargs['current_host'][1]

    def _connect_smtp(self, current_host):
        self._smtp.connect(current_host[1])

    def _disconnect_smtp(self):
        self._smtp.quit()