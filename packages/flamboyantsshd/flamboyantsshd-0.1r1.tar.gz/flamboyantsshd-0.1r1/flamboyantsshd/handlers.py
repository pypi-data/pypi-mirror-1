"Failure handlers"

from socket import inet_aton as ip2long
import subprocess

class Handler(object):
    def __init__(self, penalties, tolerance):
        self.penalties = penalties
        self.tolerance = tolerance
        # abusers is a dict with '<source>': <abuses>
        self.abusers = {}

class IPTables(Handler):
    chain_name = "ABUSERS"
    #recreate_chain = True  # Recreate chain each start-up.
    recreate_chain = False  # Recreate chain each start-up.
    abuse_target = "DROP"  # Send abusers to DROP target.

    def __init__(self, *a, **kw):
        super(IPTables, self).__init__(*a, **kw)

        self.banned = []

        if self.recreate_chain:
            self._ipt("-X", self.chain_name)  # Delete old chain.
            self._ipt("-N", self.chain_name)  # Create new chain.
        else:
            self._ipt("-F", self.chain_name)  # Just flush all rules.

        self._ipt("-A", self.chain_name, "-j", "RETURN")   # Add return fallback.

    def _ipt(self, *a):
        print "iptables", ' '.join(a)
        subprocess.Popen((("iptables",) + tuple(a))).wait()

    def ban(self, who):
        long_addr = ip2long(who)
        if long_addr not in self.banned:
            self._ipt("-I", self.chain_name, "-s", who, "-j", self.abuse_target)
            self.banned.append(ip2long(who))

    def abused(self, source, penalty=1):
        penalties = self.abusers[source] = self.abusers.get(source, self.tolerance.base_penalty) + penalty
        return penalties

    def invalid_user(self, user=None, source=None):
        if self.abused(ip2long(source), self.penalties.invalid_user) > self.tolerance.invalid_user:
            self.ban(source)

    def password_failure(self, user=None, source=None):
        if self.abused(ip2long(source), self.penalties.password_failure) > self.tolerance.password_failure:
            self.ban(source)

class DebugHandler(Handler):
    def __getattr__(self, attr):
        def f(*a, **kw):
            print "debug", attr, a, kw
        return f
