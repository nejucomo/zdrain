#!/usr/bin/env python

import sys
import argparse
import subprocess
import simplejson
from decimal import Decimal


MINCONF = 6


def main(args=sys.argv[1:]):
    """
    Drain all funds from input addresses to output addresses.
    """
    opts = parse_args(args)
    with file(opts.MAPJSON) as f:
        mapping = simplejson.load(f, use_decimal=True)

    cli = ZcashCli(opts.DATADIR)
    balances = cli.get_balances()
    for (src, dst) in mapping.iteritems():
        cli.z_sendmany_blocking(src, dst, balances[src])


def parse_args(args):
    p = argparse.ArgumentParser(description=main.__doc__)

    p.add_argument(
        '--datadir',
        dest='DATADIR',
        help='Zcash datadir.',
        default=os.path.expanduser('~/.zcash'),
        help='Zcash datadir.')

    p.add_argument(
        'MAPJSON',
        help='Path to JSON file with {... "sourceaddr": "destaddr" ...}')

    return p.parse_args(args)


class ZcashCli (object):
    def __init__(self, datadir):
        self._datadir = datadir

    def z_sendmany_blocking(self, src, dst, amount):
        print 'Sending from {} to {}: {} ZEC'.format(src, dst, amount)
        opid = self._call_rpc(
            'z_sendmany',
            src,
            {"address": dst, "amount": amount},
            verbose=True)

        statinfo = self._wait_for_op_status(opid)
        if statinfo['status'] != 'success':
            raise Exception(simplejson.dumps(statinfo))

        self._wait_for_confirmation(txid)
        print 'Confirmed: {}'.format(txid)

    def get_balances(self, taddr):
        balances = AccumulatorDict()
        self._get_taddr_balances(balances)
        self._get_zaddr_balances(balances)
        return balances

    def _wait_for_op_status(self, opid):
        statinfo = self._call_rpc_json(
            'z_getoperationstatus',
            [opid])
        while statinfo['status'] == 'executing':
            time.sleep(13)
            statinfo = self._call_rpc_json(
                'z_getoperationstatus',
                [opid])
        return statinfo

    def _wait_for_confirmation(self, txid):
        txinfo = self._call_rpc_json('gettransaction', txid)
        while txinfo['confirmations'] < MINCONF:
            time.sleep(113)
            txinfo = self._call_rpc_json('gettransaction', txid)

    def _get_taddr_balances(self, balances):
        for entry in self._call_rpc_json('listunspent', '1', '9' * 10):
            if entry['spendable']:
                taddr = entry['address']
                amount = entry['amount']
                assert isinstance(amount, Decimal), (amount, entry)
                balances.add_to(taddr, amount)

    def _get_zaddr_balances(self, balances):
        for zaddr in self._call_rpc_json('z_listaddresses'):
            amount = self._call_rpc_json('z_getbalance', zaddr)
            balances.add_to(zaddr, amount)

    def _call_rpc(self, *args, **kw):
        verbose = kw.pop('verbose', False)
        assert not kw, (args, kw)

        def encode_arg(a):
            if type(a) is str:
                return a
            else:
                return simplejson.dumps(a, use_decimal=True)

        args = (
            [
                'zcash',
                '-datadir=' + self._datadir,
            ] + [
                encode_arg(arg)
                for arg in args
            ]
        )
        if verbose:
            print 'Executing: {!r}'.format(args)
        return subprocess.check_output(args)

    def _call_rpc_json(self, *args):
        return simplejson.loads(self._call_rpc(*args), use_decimal=True)


class AccumulatorDict (dict):
    def __get__(self, key):
        return self.get(key, Decimal(0))

    def add_to(self, key, amount):
        self[key] = self[key] + amount


if __name__ == '__main__':
    main()
