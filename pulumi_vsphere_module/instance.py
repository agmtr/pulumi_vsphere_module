import os
import pulumi_vsphere as vsphere
from pulumi import ComponentResource, ResourceOptions, export
from jinja2 import Template
from base64 import b64encode

METADATA_TEMPLATE = """
instance-id: "iid-{{ name }}"
local-hostname: {{ name }}
public-keys:
  - {{ ssh_key }}

network:
  version: 2
  ethernets:
    {% for network in networks %}
    {{ network.interface }}:
      {% if network.ip_address %}
      addresses:
        - {{ network.ip_address }}
      gateway4: {{ network.gateway if network.gateway else '.'.join(network.ip_address.split('/')[0].split('.')[:-1]) + '.1' }}
      nameservers:
        addresses: {{ network.dns_servers if network.dns_servers else ['8.8.8.8', '1.1.1.1'] }}
      {% else %}
      dhcp4: true
      {% endif %}
    {% endfor %}
"""


class NetworkArgs:
    def __init__(
            self,
            name: str = "vm-lan-1",
            interface: str = "ens192",
            ip_address: str = "dhcp",
            gateway: str = None,
            dns_servers: list = None,
    ):
        self.name = name
        self.interface = interface
        self.ip_address = ip_address
        self.gateway = gateway
        self.dns_servers = dns_servers


class InstanceArgs:
    def __init__(
            self,
            datacenter: str = "Datacenter",
            cluster: str = "dell-cluster-1",
            datastore: str = "nfs_default_1",
            template: str = "rocky-9-template",
            cpus: int = 1,
            memory: int = 1024,
            disks: dict = None,
            ssh_key: str = "~/.ssh/id_ed25519.pub",
            networks: list = None,
            userdata_file: str = "userdata.yaml"
    ):
        if networks is None:
            networks = [
                NetworkArgs(name="vm-lan-1", ip_address="dhcp"),
            ]
        self.ssh_key = open(os.path.expanduser(ssh_key)).read().strip()
        self.datacenter = vsphere.get_datacenter(name=datacenter)
        self.cluster = vsphere.get_compute_cluster(name=cluster, datacenter_id=self.datacenter.id)
        self.datastore = vsphere.get_datastore(name=datastore, datacenter_id=self.datacenter.id)
        self.template = vsphere.get_virtual_machine(name=template, datacenter_id=self.datacenter.id)
        self.cpus = cpus
        self.memory = memory
        self.disks = disks if disks else self.default_disks()
        self.userdata = self.read_userdata(userdata_file) if userdata_file else None

        self.networks = networks

    def default_disks(self):
        return {disk.label: disk.size for disk in self.template.disks}

    def read_userdata(self, userdata_file):
        if userdata_file and os.path.exists(userdata_file):
            with open(userdata_file, 'r') as file:
                return file.read()
        return None

    def generate_metadata(self, name, ssh_key, networks):
        template = Template(METADATA_TEMPLATE)
        return template.render(name=name, ssh_key=ssh_key, networks=networks)


class Instance(ComponentResource):
    def __init__(self, name, args: InstanceArgs, opts: ResourceOptions = None):
        super().__init__("vsphere:modules:Instance", name, None, opts)

        self.metadata = args.generate_metadata(name, args.ssh_key, args.networks)

        network_ids = [vsphere.get_network(name=network.name, datacenter_id=args.datacenter.id).id
                       for network in args.networks]

        extra_config = {
            "guestinfo.metadata": b64encode(self.metadata.encode()).decode(),
            "guestinfo.metadata.encoding": "base64",
        }

        if args.userdata:
            extra_config.update({
                "guestinfo.userdata": b64encode(args.userdata.encode()).decode(),
                "guestinfo.userdata.encoding": "base64",
            })

        self.instance = vsphere.VirtualMachine(
            resource_name=name,
            args=vsphere.VirtualMachineArgs(
                resource_pool_id=args.cluster.resource_pool_id,
                datastore_id=args.datastore.id,
                num_cpus=args.cpus,
                memory=args.memory,
                disks=[
                    vsphere.VirtualMachineDiskArgs(
                        label=label,
                        size=size,
                        unit_number=int(idx),
                        eagerly_scrub=args.template.disks[0].eagerly_scrub,
                        thin_provisioned=args.template.disks[0].thin_provisioned
                    )
                    for idx, (label, size) in enumerate(args.disks.items())
                ],
                network_interfaces=[
                    vsphere.VirtualMachineNetworkInterfaceArgs(
                        network_id=network_id,
                        adapter_type=args.template.network_interfaces[0].adapter_type,
                    )
                    for network_id in network_ids
                ],
                clone=vsphere.VirtualMachineCloneArgs(
                    template_uuid=args.template.id,
                ),
                guest_id=args.template.guest_id,
                firmware=args.template.firmware,
                extra_config=extra_config
            ),
            opts=ResourceOptions(ignore_changes=["hvMode", "eptRviMode"])
        )
        export("instance_ip", self.instance.default_ip_address)
        self.register_outputs({})
