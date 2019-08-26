#!/usr/bin/env python

import netsnmp
import re
import argparse
import sys

pattern = 'enterprises.14179.2.2.1.1.3'
index_ap_name = '.1.3.6.1.4.1.14179.2.2.1.1.3'
index_ap_clients = '.1.3.6.1.4.1.14179.2.2.13.1.4'

# NAGIOS return codes
OK       = 0
WARNING  = 1
CRITICAL = 2
UNKNOWN  = 3

def get_list_ap_names(desthost, snmp_community):
  var = netsnmp.Varbind(index_ap_name)
  res = netsnmp.snmpwalk(var, Version=2, DestHost=desthost, Community=snmp_community)
  list_ap_names = []
  for name in res:
    list_ap_names.append(name)
  return list_ap_names

def get_tag_ap(ap_name, desthost, snmp_community):
  var = netsnmp.VarList(netsnmp.Varbind(index_ap_name))
  res = netsnmp.snmpwalk(var, Version=2, DestHost=desthost, Community=snmp_community)
  list_ap = get_list_ap_names(desthost, snmp_community)
  if ap_name in list_ap:
    for ap in var:
      if ap_name == ap.val:
        return ap.tag
  else:
      print('UNKNOWN - The AP {} does not exist.'.format(ap_name))
      sys.exit(UNKNOWN)

def get_number_clients_ap(ap_name, desthost, snmp_community):
  tag = get_tag_ap(ap_name, desthost, snmp_community)
  oid = re.split(pattern, tag)
  full_oid = index_ap_clients + oid[1]
  req = netsnmp.snmpwalk(full_oid, Version=2, DestHost=desthost, Community=snmp_community)
  req = map(int, req)
  return sum(req)

def main():
  parser = argparse.ArgumentParser(description='Display number of clients of given AP')
  parser._optionals.title = "Options"
  parser.add_argument('-H', '--hostname', nargs=1, required=True, help='FQDN or IP address of the AP Controller', dest='hostname', type=str)
  parser.add_argument('-C', '--community', nargs=1, required=True, help='SNMP community', dest='snmp_community', default='public', type=str)
  parser.add_argument('-n', '--name', nargs=1, required=False, help='name of the AP', dest='ap_name', type=str)
  parser.add_argument('-l', '--list', required=False, help='list of all AP', dest='list_ap', action='store_true')
  args = parser.parse_args()
  hostname = args.hostname[0]
  snmp_community = args.snmp_community[0]
  if args.ap_name is not None and not args.list_ap:
    ap_name = args.ap_name[0]
    res = get_number_clients_ap(ap_name, hostname, snmp_community)
    print('OK - The AP {} has {} client(s) connected. | number_clients={}'.format(ap_name, res, res))
    sys.exit(OK)
  elif args.ap_name is None and args.list_ap:
    list_ap = args.list_ap
    print('\n'.join(get_list_ap_names(hostname, snmp_community)))
  else:
    parser.print_help()

if __name__ == "__main__":
  main()
