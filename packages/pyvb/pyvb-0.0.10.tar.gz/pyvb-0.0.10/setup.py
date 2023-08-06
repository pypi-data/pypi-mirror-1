#!/usr/bin/python

def write_arg(cmd, basename, filename):
    argname = os.path.splitext(basename)[0]
    value = getattr(cmd.distribution, argname, None)
    if value is not None:
        value = '\n'.join(value)+'\n'
    cmd.write_or_delete_file(argname, filename, value)


from setuptools import setup, find_packages
setup(
    name = "pyvb",
    version = "0.0.10",
    packages = find_packages('src'),
    install_requires = ['turbogears'],
    package_dir = {'':'src'},
    scripts=[],
    zip_safe=False,
    author = "Adam Boduch",
    author_email = "adam@enomaly.com",
    description = "Python VirtualBox API.",
    license = "GPL",
    url = "http://enomalism.com/api/pyvb/",
    entry_points = {'pyvb.vb':['.VB=pyvb.vb:VB'],\
                    'pyvb.vm':['.vbVmParser=pyvb.vm.vbVmParser',\
                               '.vbVM=pyvb.vm.vbVM'],\
                    'pyvb.hdd':['.vbHddParser=pyvb.hdd.vbVmParser',\
                                '.vbHdd=pyvb.hdd.vbHdd'],\
                    'pyvb.constants':\
                    ['.VB_COMMAND=pyvb.constants.VB_COMMAND',\
                     '.VB_COMMAND_LIST_VMS=pyvb.constants.VB_COMMAND_LIST_VMS',\
                     '.VB_COMMAND_LIST_OSTYPES=pyvb.constants.VB_COMMAND_LIST_OSTYPES',\
                     '.VB_COMMAND_LIST_HOSTDVDS=pyvb.constants.VB_COMMAND_LIST_HOSTDVDS',\
                     '.VB_COMMAND_LIST_DVDS=pyvb.constants.VB_COMMAND_LIST_DVDS',\
                     '.VB_COMMAND_LIST_HDDS=pyvb.constants.VB_COMMAND_LIST_HDDS',\
                     '.VB_COMMAND_SHOWVMINFO=pyvb.constants.VB_COMMAND_SHOWVMINFO',\
                     '.VB_COMMAND_SHOWVDIINFO=pyvb.constants.VB_COMMAND_SHOWVDIINFO',\
                     '.VB_COMMAND_STARTVM=pyvb.constants.VB_COMMAND_STARTVM',\
                     '.VB_COMMAND_CONTROLVM=pyvb.constants.VB_COMMAND_CONTROLVM',\
                     '.VB_RE_NAME=pyvb.constants.VB_RE_NAME',\
                     '.VB_RE_GUESTOS=pyvb.constants.VB_RE_GUESTOS',\
                     '.VB_RE_UUID=pyvb.constants.VB_RE_UUID',\
                     '.VB_RE_UUID2=pyvb.constants.VB_RE_UUID2',\
                     '.VB_RE_CONFIGFILE=pyvb.constants.VB_RE_CONFIGFILE',\
                     '.VB_RE_MEMORYSIZE=pyvb.constants.VB_RE_MEMORYSIZE',\
                     '.VB_RE_VRAMSIZE=pyvb.constants.VB_RE_VRAMSIZE',\
                     '.VB_RE_BOOTMENUMODE=pyvb.constants.VB_RE_BOOTMENUMODE',\
                     '.VB_RE_ACPI=pyvb.constants.VB_RE_ACPI',\
                     '.VB_RE_IOACPI=pyvb.constants.VB_RE_IOACPI',\
                     '.VB_RE_TIMEOFFSET=pyvb.constants.VB_RE_TIMEOFFSET',\
                     '.VB_RE_VIRTEXT=pyvb.constants.VB_RE_VIRTEXT',\
                     '.VB_RE_STATE=pyvb.constants.VB_RE_STATE',\
                     '.VB_RE_STATE2=pyvb.constants.VB_RE_STATE2',\
                     '.VB_RE_MONITORCOUNT=pyvb.constants.VB_RE_MONITORCOUNT',\
                     '.VB_RE_FLOPPY=pyvb.constants.VB_RE_FLOPPY',\
                     '.VB_RE_PRIMARYMASTER=pyvb.constants.VB_RE_PRIMARYMASTER',\
                     '.VB_RE_DVD=pyvb.constants.VB_RE_DVD',\
                     '.VB_RE_NIC1=pyvb.constants.VB_RE_NIC1',\
                     '.VB_RE_NIC2=pyvb.constants.VB_RE_NIC2',\
                     '.VB_RE_NIC3=pyvb.constants.VB_RE_NIC3',\
                     '.VB_RE_NIC4=pyvb.constants.VB_RE_NIC4',\
                     '.VB_RE_UART1=pyvb.constants.VB_RE_UART1',\
                     '.VB_RE_UART2=pyvb.constants.VB_RE_UART2',\
                     '.VB_RE_AUDIO=pyvb.constants.VB_RE_AUDIO',\
                     '.VB_RE_CLIPBOARDMODE=pyvb.constants.VB_RE_CLIPBOARDMODE',\
                     '.VB_RE_SHAREDFOLDERS=pyvb.constants.VB_RE_SHAREDFOLDERS',\
                     '.VB_RE_ID=pyvb.constants.VB_RE_ID',\
                     '.VB_RE_DESCRIPTION=pyvb.constants.VB_RE_DESCRIPTION',\
                     '.VB_RE_PATH=pyvb.constants.VB_RE_PATH',\
                     '.VB_RE_ACCESSIBLE=pyvb.constants.VB_RE_ACCESSIBLE',\
                     '.VB_RE_STORAGETYPE=pyvb.constants.VB_RE_STORAGETYPE',\
                     '.VB_RE_USAGE=pyvb.constants.VB_RE_USAGE',\
                     '.VB_RE_SHAREDFOLDER_NAME=pyvb.constants.VB_RE_SHAREDFOLDER_NAME',\
                     '.VB_RE_SHAREDFOLDER_PATH=pyvb.constants.VB_RE_SHAREDFOLDER_PATH',\
                     '.VB_RE_STATE_NAME=pyvb.constants.VB_RE_STATE_NAME',\
                     '.VB_RE_STATE_DATE=pyvb.constants.VB_RE_STATE_DATE',\
                     '.VB_RE_REGISTERED=pyvb.constants.VB_RE_REGISTERED',\
                     '.VB_RE_SIZE=pyvb.constants.VB_RE_SIZE',\
                     '.VB_RE_CURRENT_DISK_SIZE=pyvb.constants.VB_RE_CURRENT_DISK_SIZE'],\
                    'pyvb.parser':['.vbParser=pyvb.parser.vbParser'],\
                    'pyvb.dvd':['.vbHostDvdParser=pyvb.dvd.vbHostDvdParser',\
                                '.vbDvdParser=pyvb.dvd.vbDvdParser',\
                                '.vbHostDvd=pyvb.dvd.vbHostDvd',\
                                '.vbDvd=pyvb.dvd.vbDvd'],\
                    'pyvb.ostype':['.vbOsTypeParser=pyvb.ostype.vbOsTypeParser',\
                                   '.vbOsType=pyvb.ostype.vbOsType'],\
                    'pyvb.sharedfolder':['.vbSharedFolderParser=pyvb.sharedfolder.vbSharedFolderParser',\
                                         '.vbSharedFolder=pyvb.sharedfolder.vbSharedFolder'],\
                    'pyvb.state':['.vbStateParser=pyvb.state.vbStateParser',\
                                  '.vbState=pyvb.state.vbState'],\
                    'pyvb.server':['.vbRestServer=pyvb.server.vbRestServer']}
)
