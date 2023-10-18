"""A Python Pulumi program"""

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
        )
    ],
    networks=[
        NetworkArgs(
            ip_address='10.0.1.11'
        )
    ],
    ssh_keys=[
        './id_ed25519.pub',
    ]
)

instance_1 = Instance("vm-1", instance_args)
