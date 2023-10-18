## pulumi_vsphere_module

A module for creating virtual machines on VMware vSphere using Pulumi.

### Installation

```bash
pip install git+https://github.com/agmtr/pulumi_vsphere_module.git
```

### Usage

```python
from pulumi_vsphere_module import Instance, InstanceArgs, NetworkArgs

# Define the parameters for the instance creation
network_args = NetworkArgs(name="vm-lan-1", ip_address="dhcp")
instance_args = InstanceArgs(
    datacenter="Datacenter",
    cluster="dell-cluster-1",
    datastore="nfs_default_1",
    template="rocky-9-template",
    cpus=1,
    memory=1024,
    ssh_key="~/.ssh/id_ed25519.pub",
    networks=[network_args],
    userdata_file="userdata.yaml"
)

# Create the instance
instance = Instance("my-instance", instance_args)
```

### License

MIT
