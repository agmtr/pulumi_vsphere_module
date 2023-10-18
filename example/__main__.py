"""A Python Pulumi program"""

from pulumi_vsphere_module.instance import Instance, InstanceArgs, NetworkArgs

Instance(
    name="test-instance",
    args=InstanceArgs(
        cpus=2,
        memory=2048,
        disks={
            "disk0": 20,
            "disk1": 30
        },
        networks=[
            NetworkArgs(
                ip_address="10.102.11.200"
            )
        ],
        template="rocky-9-template",
        userdata_file="userdata.yaml"
    )
)
