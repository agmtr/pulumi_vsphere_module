# pulumi_vsphere_module

A module for creating virtual machines on VMware vSphere using Pulumi.

## Prerequisites

- Pulumi CLI installed.
- Necessary environment variables set (VSPHERE_USER, VSPHERE_PASSWORD, VSPHERE_SERVER, VSPHERE_ALLOW_UNVERIFIED_SSL=true).
- A vSphere environment with required resources (datastores, networks, templates, etc.).

## Usage

```bash
pulumi login --local
pulumi new python
source venv/bin/activate
pip install git+https://github.com/agmtr/pulumi_vsphere_module.git
```

```python
# __main__.py
from pulumi_vsphere_module.instance import Instance, InstanceArgs, NetworkArgs

# Define the parameters for the instance creation
network_args = NetworkArgs(name="vm-lan-1", ip_address="dhcp")
instance_args = InstanceArgs(
    cpus=1,
    memory=1024,
    networks=[network_args],
    template="rocky-9-template",
    userdata_file="userdata.yaml",  
    ssh_key="~/.ssh/id_ed25519.pub",
)

# Create the instance
instance = Instance("my-instance", instance_args)
```

```bash
pulumi up
```

## License

MIT
