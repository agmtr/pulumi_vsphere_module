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
pip install git+https://github.com/agmtr/pulumi_vsphere_module.git
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

## License

MIT
