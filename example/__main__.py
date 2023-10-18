"""A Python Pulumi program"""

from pulumi_vsphere_module.instance import Instance, InstanceArgs, NetworkArgs

Instance(
    name="test-instance",
    args=InstanceArgs(
        cpus=2,
        memory=2048,
        networks=[
            NetworkArgs(
                ip_address="10.102.11.200"
            )
        ]
    )
)
