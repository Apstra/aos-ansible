#
# Copyright (c) 2017 Apstra Inc, <community@apstra.com>
#
# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by
# Ansible still belong to the author of the module, and may assign their own
# license to the complete work.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

"""
This module adds shared support for Apstra AOS modules

In order to use this module, include it as part of your module

from ansible.module_utils.aos import *

"""

import ipaddress
from library.aos import aos_delete, aos_put, aos_get, aos_post


class Pool(object):
    def __init__(self, module, session, check_mode):

        self.module = module
        self.session = session
        self.check_mode = check_mode

    def validate(self, ranges):
        raise NotImplementedError("Inherit and implement")

    def create(self, ranges, name):
        raise NotImplementedError("Inherit and implement")

    def update(self, name, existing_uuid, existing_ranges, new_ranges):
        raise NotImplementedError("Inherit and implement")

    def delete(self, pool_id):
        if not self.check_mode:
            resp = aos_delete(self.session, self.resource_uri, pool_id)

            return self.module_exit(error=[],
                                    name='', uuid=pool_id,
                                    value=resp, changed=True)

    def find_by_name(self, name):
        if self.check_mode:
            return None

        for r in aos_get(self.session, self.resource_uri)['items']:
            if r["display_name"] == name:
                return r

    def find_by_id(self, uuid):
        if self.check_mode:
            return None

        return aos_get(self.session, "{}/{}".format(self.resource_uri, uuid))

    def get_ranges(self, ranges):
        return [{"first": r[0], "last": r[1]} for r in ranges]

    def get_subnets(self, subnets):
        return [{"network": r} for r in subnets]

    def module_exit(self, error, name, uuid, value, changed=True):

        if error:
            return self.module.fail_json(msg=error)

        return self.module.exit_json(changed=changed,
                                     name=name,
                                     id=uuid,
                                     value=value)


class AsnPool(Pool):
    resource_uri = "resources/asn-pools"

    def validate(self, ranges):
        errors = []

        for i, asn_range in enumerate(ranges, 1):
            if not isinstance(asn_range, list):
                errors.append("Invalid range: must be a list")
            elif len(asn_range) != 2:
                errors.append("Invalid range: must be a list of 2 members")
            elif any(map(lambda r: not isinstance(r, int), asn_range)):
                errors.append("Invalid range: Expected integer values")
            elif asn_range[1] <= asn_range[0]:
                errors.append("Invalid range: 2nd element must be bigger than 1st")

        return errors

    def create(self, ranges, name):
        new_pool = {
            "ranges": ranges,
            "display_name": name,
            "id": name
        }

        if not self.check_mode:
            resp = aos_post(self.session, self.resource_uri, new_pool)

            return self.module_exit(error=[], name=name, uuid=resp['id'],
                                    value=new_pool, changed=True)

    def update(self, name, existing_uuid, existing_ranges, new_ranges):
        new_pool = {
            "ranges": new_ranges,
            "display_name": name,
            "id": existing_uuid
        }

        for pool_range in existing_ranges:
            if pool_range not in new_pool['ranges']:
                new_pool['ranges'].append({'first': pool_range['first'],
                                           'last': pool_range['last']})

        if not self.check_mode:
            aos_put(
                self.session,
                "{}/{}".format(self.resource_uri, existing_uuid),
                new_pool
            )

            return self.module_exit(error=[], name=name, uuid=existing_uuid,
                                    value=new_pool, changed=True)

    def __str__(self):
        return "ASN pool"


class VniPool(Pool):
    resource_uri = "resources/vni-pools"

    def validate(self, ranges):
        errors = []

        for i, vni_range in enumerate(ranges, 1):
            if not isinstance(vni_range, list):
                errors.append("Invalid range: must be a list")
            elif len(vni_range) != 2:
                errors.append("Invalid range: must be a list of 2 members")
            elif any(map(lambda r: not isinstance(r, int), vni_range)):
                errors.append("Invalid range: Expected integer values")
            elif vni_range[1] <= vni_range[0]:
                errors.append("Invalid range: 2nd element must be bigger than 1st")
            elif vni_range[0] <= 4095 or vni_range[1] >= 16777213:
                errors.append("Invalid range: must be a valid range between 4096"
                              " and 16777214")

        return errors

    def create(self, ranges, name):
        new_pool = {
            "ranges": ranges,
            "display_name": name,
            "id": name
        }

        if not self.check_mode:
            resp = aos_post(self.session, self.resource_uri, new_pool)

            return self.module_exit(error=[], name=name, uuid=resp['id'],
                                    value=new_pool, changed=True)

    def update(self, name, existing_uuid, existing_ranges, new_ranges):
        new_pool = {
            "ranges": new_ranges,
            "display_name": name,
            "id": existing_uuid
        }

        for pool_range in existing_ranges:
            if pool_range not in new_pool['ranges']:
                new_pool['ranges'].append({'first': pool_range['first'],
                                           'last': pool_range['last']})

        if not self.check_mode:
            aos_put(
                self.session,
                "{}/{}".format(self.resource_uri, existing_uuid),
                new_pool
            )

            return self.module_exit(error=[], name=name, uuid=existing_uuid,
                                    value=new_pool, changed=True)

    def __str__(self):
        return "VNI pool"


class IpPool(Pool):
    def __init__(self, module, session, addr_type, check_mode):
        self.addr_type = addr_type
        super(IpPool, self).__init__(module, session, check_mode)

        if self.addr_type == 4:
            self.resource_uri = "resources/ip-pools"
        elif self.addr_type == 6:
            self.resource_uri = "resources/ipv6-pools"
        else:
            self.module_exit(error="Invalid addr_type", name='',
                             uuid='', value='', changed=False)

    def validate(self, subnets):
        errors = []
        for i, subnet in enumerate(subnets, 1):
            try:
                results = ipaddress.ip_network(subnet)
                if results.version != self.addr_type:
                    errors.append("{} is not a valid ipv{} subnet"
                                  .format(subnet, self.addr_type))

            except ValueError:
                errors.append("Invalid subnet: {}".format(subnet))

        return errors

    def create(self, subnets, name):
        new_pool = {
            "subnets": subnets,
            "display_name": name,
            "id": name
        }

        if not self.check_mode:
            resp = aos_post(self.session, self.resource_uri, new_pool)

            return self.module_exit(error=[], name=name, uuid=resp['id'],
                                    value=new_pool, changed=True)

    def update(self, name, existing_uuid, existing_subnets, new_subnets):
        new_pool = {
            "subnets": new_subnets,
            "display_name": name,
            "id": existing_uuid
        }

        for ip_subnet in existing_subnets:
            if ip_subnet['network'] not in new_pool['subnets']:
                new_pool['subnets'].append({'network': ip_subnet['network']})

        if not self.check_mode:
            aos_put(
                self.session,
                "{}/{}".format(self.resource_uri, existing_uuid),
                new_pool
            )

            return self.module_exit(error=[], name=name, uuid=existing_uuid,
                                    value=new_pool, changed=True)

    def __str__(self):
        return "ip pool"
