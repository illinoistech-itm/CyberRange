from proxmoxer import ProxmoxAPI
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
proxmox = ProxmoxAPI(config['DEFAULT']['url'], user=config['DEFAULT']['user'], password=config['DEFAULT']['pass'], verify_ssl=False)

prxmx35 = proxmox.nodes("system35").qemu.get()
prxmx43 = proxmox.nodes("system43").qemu.get()

runningvms = []
runningwithtagsvms = []
# Loop through the first node to get all of the nodes that are of status running and that have the tag of the user
for vm in prxmx35:
    if vm['status'] == 'running' and vm['tags'].split(';')[0] == '1732922922':
        runningvms.append(vm)


# Loop through those running VMs to then get networking/IP information
for vm in runningvms:
    runningwithtagsvms.append(proxmox.nodes("system35").qemu(vm['vmid']).agent("network-get-interfaces").get())

for x in range(len(runningwithtagsvms)):
    for y in range(len(runningwithtagsvms[x]['result'])):
        print(runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address']) if "192.168.100." in runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address'] else None

