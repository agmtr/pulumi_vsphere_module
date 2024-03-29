# instance.py

import os
import yaml
import pulumi_vsphere as vsphere
from pulumi import ComponentResource, ResourceOptions, export
from base64 import b64encode
from jinja2 import Environment, FileSystemLoader
from dataclasses import dataclass, field
from typing import List

template_loader = FileSystemLoader(searchpath=os.path.dirname(os.path.abspath(__file__)))
template_env = Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True)

METADATA_TEMPLATE = template_env.get_template("metadata.yaml.j2")
USERDATA_TEMPLATE = template_env.get_template("userdata.yaml.j2")


@dataclass
class DiskArgs:
    label: str = "root"
    size: int = 20
    eagerly_scrub: bool = False
    thin_provisioned: bool = True
    mount_point: str = None


@dataclass
class NetworkArgs:
    name: str = "vm-lan-1"
    interface: str = "ens192"
    ip_address: str = "dhcp"
    gateway: str = None
    dns_servers: List[str] = field(default_factory=lambda: [])


@dataclass
class InstanceArgs:
    datacenter: str = "Datacenter"
    cluster: str = "dell-cluster-1"
    datastore: str = "nfs_default_1"
    template: str = "rocky-9-template"
    cpus: int = 1
    memory: int = 1024
    disks: List[DiskArgs] = field(default_factory=lambda: [DiskArgs()])
    ssh_keys: List[str] = field(default_factory=lambda: ["~/.ssh/id_ed25519.pub"])
    networks: List[NetworkArgs] = field(default_factory=lambda: [NetworkArgs()])
    enable_disk_uuid: bool = True
    userdata_file: str = None
    custom_extra_config: dict = None
    wait_for_guest_net_timeout: int = 300


def load_ssh_keys(file_paths):
    ssh_keys = []
    for file_path in file_paths:
        expanded_path = os.path.expanduser(file_path)
        with open(expanded_path, 'r') as f:
            ssh_keys.append(f.read().strip())
    return ssh_keys


def generate_metadata(name, ssh_keys, networks):
    return METADATA_TEMPLATE.render(name=name, ssh_keys=ssh_keys, networks=networks)


def generate_userdata(disks, userdata_file=None):
    userdata_generated = yaml.safe_load(USERDATA_TEMPLATE.render(disks=disks)) or {}
    if userdata_file:
        with open(userdata_file, 'r') as f:
            custom_yaml = yaml.safe_load(f)
            userdata_generated.update(custom_yaml)

    userdata_final = "#cloud-config\n" + yaml.dump(userdata_generated)
    return userdata_final


class Instance(ComponentResource):
    def __init__(self, name, args: InstanceArgs, opts: ResourceOptions = None):
        super().__init__("vsphere:modules:Instance", name, None, opts)

        self._prepare_resources(args)
        self._generate_extra_config(name, args)
        self._create_instance(name, args)

        export("instance_ip", self.instance.default_ip_address)
        self.register_outputs({})

    def _prepare_resources(self, args):
        self.datacenter = vsphere.get_datacenter(name=args.datacenter)
        self.cluster = vsphere.get_compute_cluster(name=args.cluster, datacenter_id=self.datacenter.id)
        self.datastore = vsphere.get_datastore(name=args.datastore, datacenter_id=self.datacenter.id)
        self.template = vsphere.get_virtual_machine(name=args.template, datacenter_id=self.datacenter.id)
        self.networks = [vsphere.get_network(name=network.name, datacenter_id=self.datacenter.id) for network in
                         args.networks]

    def _generate_extra_config(self, name, args):
        ssh_keys = load_ssh_keys(args.ssh_keys)
        metadata = generate_metadata(name, ssh_keys, args.networks)
        userdata = generate_userdata(args.disks, args.userdata_file)

        if not args.custom_extra_config:
            self.extra_config = {
                "guestinfo.metadata": b64encode(metadata.encode()).decode(),
                "guestinfo.metadata.encoding": "base64",
                "guestinfo.userdata": b64encode(userdata.encode()).decode(),
                "guestinfo.userdata.encoding": "base64",
            }
        else:
            self.extra_config = args.custom_extra_config

    def _create_instance(self, name, args):
        self.instance = vsphere.VirtualMachine(
            resource_name=name,
            args=vsphere.VirtualMachineArgs(
                name=name,
                resource_pool_id=self.cluster.resource_pool_id,
                datastore_id=self.datastore.id,
                num_cpus=args.cpus,
                memory=args.memory,
                disks=[
                    vsphere.VirtualMachineDiskArgs(
                        label=disk.label,
                        size=disk.size,
                        unit_number=int(idx),
                        eagerly_scrub=disk.eagerly_scrub,
                        thin_provisioned=disk.thin_provisioned
                    )
                    for idx, disk in enumerate(args.disks)
                ],
                network_interfaces=[
                    vsphere.VirtualMachineNetworkInterfaceArgs(
                        network_id=network.id,
                    )
                    for network in self.networks
                ],
                clone=vsphere.VirtualMachineCloneArgs(
                    template_uuid=self.template.id,
                ),
                guest_id=self.template.guest_id,
                firmware=self.template.firmware,
                extra_config=self.extra_config,
                enable_disk_uuid=args.enable_disk_uuid,
                wait_for_guest_net_timeout=args.wait_for_guest_net_timeout
            ),
            opts=ResourceOptions(ignore_changes=["hvMode", "eptRviMode"])
        )
