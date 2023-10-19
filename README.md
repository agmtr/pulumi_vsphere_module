# pulumi_vsphere_module

A module for creating virtual machines on VMware vSphere using Pulumi.

## Prerequisites

- Pulumi CLI installed.
- Necessary environment variables set (VSPHERE_USER, VSPHERE_PASSWORD, VSPHERE_SERVER, VSPHERE_ALLOW_UNVERIFIED_SSL=true).
- A vSphere environment with required resources (datastores, networks, templates, etc.).

## Usage

```bash
pulumi login --local (or pulumi login)
pulumi new python
source venv/bin/activate
pip install git+https://github.com/agmtr/pulumi_vsphere_module.git@<VERSION>
```

```python
# __main__.py
from pulumi_vsphere_module.instance import Instance, InstanceArgs, DiskArgs, NetworkArgs

instance_args = InstanceArgs(
    cpus=4,
    memory=4 * 1024,
    disks=[
        DiskArgs(
            label='root',
            size=20,
        ),
        DiskArgs(
            label='logs',
            size=50,
            mount_point="/var/log"
        ),
        DiskArgs(
            label="data",
            size=500,
            mount_point="/var/data"
        )
    ],
    networks=[
        NetworkArgs(
            ip_address='10.0.1.11'
        )
    ],
    ssh_keys=[
        './id_ed25519.pub',
    ],
    template="rocky-8-template",
    userdata_file="./userdata.yaml"
)

instance_1 = Instance("vm-1", instance_args)
```

```bash
pulumi up
```

## Specifications
### Data Classes

DiskArgs: Configuration for VM disks. Attributes include:
- label: Disk label (default: "root")
- size: Disk size in GB (default: 20)
- eagerly_scrub: Boolean flag for disk scrubbing (default: False)
- thin_provisioned: Boolean flag for disk provisioning (default: True)
- mount_point: Disk mount point, if applicable

NetworkArgs: Configuration for VM network settings. Attributes include:
- name: Network name (default: "vm-lan-1")
- interface: Network interface (default: "ens192")
- ip_address: IP address or "dhcp" for dynamic assignment (default: "dhcp")
- gateway: Network gateway, if applicable
- dns_servers: List of DNS servers

InstanceArgs: Configuration for the VM instance itself. Attributes include:
- datacenter: Datacenter name
- cluster: Cluster name
- datastore: Datastore name
- template: VM template to use
- cpus: Number of CPUs
- memory: RAM in MB
- disks: List of DiskArgs
- ssh_keys: List of paths to SSH key files
- networks: List of NetworkArgs
- enable_disk_uuid: Boolean flag to enable disk UUID
- userdata_file: Path to an additional user data YAML file

## License

MIT
