locals { timestamp = regex_replace(timestamp(), "[- TZ:]", "") }

#packer {
#  required_plugins {
#    virtualbox = {
#      version = ">= 1.2.0"
#      source  = "github.com/hashicorp/proxmox"
#    }
#  }
#}

# source blocks are generated from your builders; a source can be referenced in
# build blocks. A build block runs provisioner and post-processors on a
# source. Read the documentation for source blocks here:
# https://www.packer.io/docs/from-1.5/blocks/source
# https://github.com/burkeazbill/ubuntu-22-04-packer-fusion-workstation/blob/master/ubuntu-2204-daily.pkr.hcl

###########################################################################################
# This is a Packer build template the edge server for lab_one
###########################################################################################
source "proxmox-iso" "lab_one_edge_server_41" {
  boot_command = [
    "e<wait>",
    "<down><down><down>",
    "<end><bs><bs><bs><bs><wait>",
    "autoinstall ds=nocloud-net\\;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/ ---<wait>",
    "<f10><wait>"
  ]
  boot_iso {
    type="scsi"
    iso_file="local:iso/${var.local_iso_name}"
    unmount=true
    iso_checksum="${var.iso_checksum}"
  }
  boot_wait = "5s"
  cores     = "${var.NUMBEROFCORES}"
  node      = "${local.NODENAME}"
  username  = "${local.USERNAME}"
  token     = "${local.PROXMOX_TOKEN}"
  cpu_type  = "host"
  disks {
    disk_size    = "${var.DISKSIZE}"
    storage_pool = "${var.STORAGEPOOL}"
    type         = "virtio"
    io_thread    = true
    format       = "raw"
  }
  http_directory    = "subiquity/http"
  http_bind_address = "10.110.0.45"
  http_port_max    = 9200
  http_port_min    = 9001
  memory           = "${var.MEMORY}"

  network_adapters {
    bridge = "vmbr0"
    model  = "virtio"
  }
  network_adapters {
    bridge = "vmbr1"
    model  = "virtio"
  }
  network_adapters {
    bridge = "vmbr2"
    model  = "virtio"
  }

  os                       = "l26"
  proxmox_url              = "${local.URL}"
  insecure_skip_tls_verify = true
  qemu_agent               = true
  cloud_init               = true
  cloud_init_storage_pool  = "local"
  # io thread option requires virtio-scsi-single controller
  scsi_controller          = "virtio-scsi-single"
  ssh_password             = "${local.SSHPW}"
  ssh_username             = "${local.SSHUSER}"
  ssh_timeout              = "22m"
  template_description     = "A Packer template for CR edge_node lab_one" 
  vm_name                  = "${var.VMNAME}"
  tags                     = "${var.TAGS}"
}

###########################################################################################
# This is a Packer build template the lab_node for lab_one
###########################################################################################
source "proxmox-iso" "lab_one_node_41" {
  boot_command = [
    "e<wait>",
    "<down><down><down>",
    "<end><bs><bs><bs><bs><wait>",
    "autoinstall ds=nocloud-net\\;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/ ---<wait>",
    "<f10><wait>"
  ]
  boot_iso {
    type="scsi"
    iso_file="local:iso/${var.local_iso_name}"
    unmount=true
    iso_checksum="${var.iso_checksum}"
  }
  boot_wait = "5s"
  cores     = "${var.NUMBEROFCORES}"
  node      = "${local.NODENAME}"
  username  = "${local.USERNAME}"
  token     = "${local.PROXMOX_TOKEN}"
  cpu_type  = "host"
  disks {
    disk_size    = "${var.DISKSIZE}"
    storage_pool = "${var.STORAGEPOOL}"
    type         = "virtio"
    io_thread    = true
    format       = "raw"
  }
  http_directory    = "subiquity/http"
  http_bind_address = "10.110.0.45"
  http_port_max    = 9200
  http_port_min    = 9001
  memory           = "${var.MEMORY}"

  network_adapters {
    bridge = "vmbr0"
    model  = "virtio"
  }
  network_adapters {
    bridge = "vmbr1"
    model  = "virtio"
  }
  network_adapters {
    bridge = "vmbr2"
    model  = "virtio"
  }

  os                       = "l26"
  proxmox_url              = "${local.URL}"
  insecure_skip_tls_verify = true
  qemu_agent               = true
  cloud_init               = true
  cloud_init_storage_pool  = "local"
  # io thread option requires virtio-scsi-single controller
  scsi_controller          = "virtio-scsi-single"
  ssh_password             = "${local.SSHPW}"
  ssh_username             = "${local.SSHUSER}"
  ssh_timeout              = "22m"
  template_description     = "A Packer template CR lab_one lab node" 
  vm_name                  = "${var.LN-VMNAME}"
  tags                     = "${var.TAGS}"
}

###########################################################################################
# This is a Packer build template the edge server for lab_one
###########################################################################################
source "proxmox-iso" "lab_one_edge_server_42" {
  boot_command = [
    "e<wait>",
    "<down><down><down>",
    "<end><bs><bs><bs><bs><wait>",
    "autoinstall ds=nocloud-net\\;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/ ---<wait>",
    "<f10><wait>"
  ]
  boot_iso {
    type="scsi"
    iso_file="local:iso/${var.local_iso_name}"
    unmount=true
    iso_checksum="${var.iso_checksum}"
  }
  boot_wait = "12s"
  cores     = "${var.NUMBEROFCORES}"
  node      = "${local.NODENAME2}"
  username  = "${local.USERNAME}"
  token     = "${local.PROXMOX_TOKEN}"
  cpu_type  = "host"
  disks {
    disk_size    = "${var.DISKSIZE}"
    storage_pool = "${var.STORAGEPOOL}"
    type         = "virtio"
    io_thread    = true
    format       = "raw"
  }
  http_directory    = "subiquity/http"
  http_bind_address = "10.110.0.45"
  http_port_max    = 9200
  http_port_min    = 9001
  memory           = "${var.MEMORY}"

  network_adapters {
    bridge = "vmbr0"
    model  = "virtio"
  }
  network_adapters {
    bridge = "vmbr1"
    model  = "virtio"
  }
  network_adapters {
    bridge = "vmbr2"
    model  = "virtio"
  }

  os                       = "l26"
  proxmox_url              = "${local.URL}"
  insecure_skip_tls_verify = true
  qemu_agent               = true
  cloud_init               = true
  cloud_init_storage_pool  = "local"
  # io thread option requires virtio-scsi-single controller
  scsi_controller          = "virtio-scsi-single"
  ssh_password             = "${local.SSHPW}"
  ssh_username             = "${local.SSHUSER}"
  ssh_timeout              = "22m"
  template_description     = "A Packer template for CR edge_node lab_one"
  vm_name                  = "${var.VMNAME}"
  tags                     = "${var.TAGS}"
}

###########################################################################################
# This is a Packer build template the lab_node for lab_one
###########################################################################################
source "proxmox-iso" "lab_one_node_42" {
  boot_command = [
    "e<wait>",
    "<down><down><down>",
    "<end><bs><bs><bs><bs><wait>",
    "autoinstall ds=nocloud-net\\;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/ ---<wait>",
    "<f10><wait>"
  ]
  boot_iso {
    type="scsi"
    iso_file="local:iso/${var.local_iso_name}"
    unmount=true
    iso_checksum="${var.iso_checksum}"
  }
  boot_wait = "12s"
  cores     = "${var.NUMBEROFCORES}"
  node      = "${local.NODENAME2}"
  username  = "${local.USERNAME}"
  token     = "${local.PROXMOX_TOKEN}"
  cpu_type  = "host"
  disks {
    disk_size    = "${var.DISKSIZE}"
    storage_pool = "${var.STORAGEPOOL}"
    type         = "virtio"
    io_thread    = true
    format       = "raw"
  }
  http_directory    = "subiquity/http"
  http_bind_address = "10.110.0.45"
  http_port_max    = 9200
  http_port_min    = 9001
  memory           = "${var.MEMORY}"

  network_adapters {
    bridge = "vmbr0"
    model  = "virtio"
  }
  network_adapters {
    bridge = "vmbr1"
    model  = "virtio"
  }
  network_adapters {
    bridge = "vmbr2"
    model  = "virtio"
  }

  os                       = "l26"
  proxmox_url              = "${local.URL}"
  insecure_skip_tls_verify = true
  qemu_agent               = true
  cloud_init               = true
  cloud_init_storage_pool  = "local"
  # io thread option requires virtio-scsi-single controller
  scsi_controller          = "virtio-scsi-single"
  ssh_password             = "${local.SSHPW}"
  ssh_username             = "${local.SSHUSER}"
  ssh_timeout              = "22m"
  template_description     = "A Packer template for CR lab_node lab_one"
  vm_name                  = "${var.LN-VMNAME}"
  tags                     = "${var.TAGS}"
}

build {
  sources = ["source.proxmox-iso.lab_one_edge_server_42","source.proxmox-iso.lab_one_edge_server_41","source.proxmox-iso.lab_one_node_42","source.proxmox-iso.lab_one_node_41"]

  ##############################################################################
  # Copying the custom configuration for Alloy to be setup to send systemd logs
  # to Loki
  #############################################################################

  provisioner "file" {
    source      = "../scripts/proxmox/jammy-services/config.alloy"
    destination = "/home/vagrant/config.alloy"
  }

  #############################################################################
  # Using the file provisioner to SCP this file to the instance 
  # Add .hcl configuration file to register an instance with Consul for dynamic
  # DNS on the third interface
  #############################################################################

  provisioner "file" {
    source      = "./system.hcl"
    destination = "/home/vagrant/"
  }

  #############################################################################
  # Copy the node-exporter-consul-service.json file to the instance move this 
  # file to /etc/consul.d/ directory so that each node can register as a 
  # service dynamically -- which Prometheus can then 
  # scape and automatically find metrics to collect
  #############################################################################

  provisioner "file" {
    source      = "../../scripts/proxmox/jammy-services/node-exporter-consul-service.json"
    destination = "/home/vagrant/"
  }

  #############################################################################
  # Copy the consul.conf file to the instance to update the consul DNS to look 
  # on the internal port of 8600 to resolve the .consul domain lookups
  #############################################################################

  provisioner "file" {
    source      = "../../scripts/proxmox/jammy-services/consul.conf"
    destination = "/home/vagrant/"
  }

  #############################################################################
  # Copy the node_exporter service file to the template so that the instance 
  # can publish its own system metrics on the metrics interface
  #############################################################################

  provisioner "file" {
    source      = "../../scripts/proxmox/jammy-services/node-exporter.service"
    destination = "/home/vagrant/"
  }

  #############################################################################
  # This is the script that will open firewall ports needed for a node to 
  # function on the the School Cloud Platform and create the default firewalld
  # zones.
  #############################################################################

  provisioner "shell" {
    execute_command = "echo 'vagrant' | {{ .Vars }} sudo -E -S sh '{{ .Path }}'"
    scripts         = ["../../scripts/proxmox/core-jammy/post_install_prxmx-firewall-configuration.sh"]
  }

  #############################################################################
  # These shell scripts are needed to create the cloud instances and register 
  # the instance with Consul DNS --- Don't edit this
  #############################################################################

  provisioner "shell" {
    execute_command = "echo 'vagrant' | {{ .Vars }} sudo -E -S sh '{{ .Path }}'"
    scripts = ["../../scripts/proxmox/core-jammy/post_install_prxmx_ubuntu_2204.sh",
      "../../scripts/proxmox/core-jammy/post_install_prxmx_start-cloud-init.sh",
      "../../scripts/proxmox/core-jammy/post_install_prxmx_install_hashicorp_consul.sh",
    "../../scripts/proxmox/core-jammy/post_install_prxmx_update_dns_for_consul_service.sh",
     "../scripts/proxmox/core-jammy/post_install_alloy_log_forwarder.sh"]
  }

  #############################################################################
  # Script to change the bind_addr in Consul to the dynamic Go lang call to
  # Interface ens20
  # https://www.consul.io/docs/troubleshoot/common-errors
  #############################################################################

  provisioner "shell" {
    execute_command = "echo 'vagrant' | {{ .Vars }} sudo -E -S sh '{{ .Path }}'"
    scripts         = ["../../scripts/proxmox/core-jammy/post_install_change_consul_bind_interface.sh"]
  }

  #############################################################################
  # Script to give a dynamic message about the consul DNS upon login
  #
  # https://ownyourbits.com/2017/04/05/customize-your-motd-login-message-in-debian-and-ubuntu/
  #############################################################################

  provisioner "shell" {
    execute_command = "echo 'vagrant' | {{ .Vars }} sudo -E -S sh '{{ .Path }}'"
    scripts         = ["../../scripts/proxmox/core-jammy/post_install_update_dynamic_motd_message.sh"]
  }

  #############################################################################
  # Script to install Prometheus Telemetry support
  #############################################################################

  provisioner "shell" {
    execute_command = "echo 'vagrant' | {{ .Vars }} sudo -E -S sh '{{ .Path }}'"
    scripts         = ["../../scripts/proxmox/core-jammy/post_install_prxmx_ubuntu_install-prometheus-node-exporter.sh"]
  }

  ########################################################################################################################
  # Copying the pyxtermjs service file into the VM
  ########################################################################################################################
 
  provisioner "file" {
    source      = "../../scripts/proxmox/labs/core/pyxtermjs.service"
    destination = "/home/vagrant/"
    only=["proxmox-iso.lab_one_edge_server_42","proxmox-iso.lab_one_edge_server_41"]  
    }

  ########################################################################################################################
  # Copying the default file needed into Nginx
  ########################################################################################################################
 
  provisioner "file" {
    source      = "../../scripts/proxmox/labs/core/nginx/default"
    destination = "/home/vagrant/"
    only=["proxmox-iso.lab_one_edge_server_42","proxmox-iso.lab_one_edge_server_41"]  
    }

  ########################################################################################################################
  # Copying the self-signed.conf into Nginx
  ########################################################################################################################
 
  provisioner "file" {
    source      = "../../scripts/proxmox/labs/core/nginx/signed.conf"
    destination = "/home/vagrant/"
    only=["proxmox-iso.lab_one_edge_server_42","proxmox-iso.lab_one_edge_server_41"]  
    }

  ########################################################################################################################
  # Script to Generate signed certificates
  ########################################################################################################################
 
  provisioner "shell" {
    execute_command = "echo 'vagrant' | {{ .Vars }} sudo -E -S sh '{{ .Path }}'"
    scripts         = ["../../scripts/proxmox/labs/core/post_install_prxmx_generate_ca.sh"]
    only=["proxmox-iso.lab_one_edge_server_42","proxmox-iso.lab_one_edge_server_41"]
  }


  #############################################################################
  # Script to move the pyxtermjs service file and enable it
  #############################################################################

  provisioner "shell" {
    execute_command = "echo 'vagrant' | {{ .Vars }} sudo -E -S sh '{{ .Path }}'"
    scripts         = ["../../scripts/proxmox/labs/core/post_install_prxmx_ubuntu_create_service_account_for_flask_app.sh",
                      "../../scripts/proxmox/labs/core/move-pyxtermjs-service.sh",
                      "../../scripts/proxmox/labs/core/install-nginx.sh",
                      "../../scripts/proxmox/labs/core/move-nginx-files.sh",
                        "../../scripts/proxmox/labs/core/post_install_prxms_install_pyxtermjs.sh",
                      "../../scripts/proxmox/labs/core/install-nmap.sh",
                      "../../scripts/proxmox/labs/core/post_install_prxmx_lab_node-firewall-open-ports.sh"]
    only=["proxmox-iso.lab_one_edge_server_42","proxmox-iso.lab_one_edge_server_41"]
  }

  #############################################################################
  # Install the lab elements on the node(s)
  #############################################################################

  provisioner "shell" {
    execute_command = "echo 'vagrant' | {{ .Vars }} sudo -E -S sh '{{ .Path }}'"
    scripts         = ["../../scripts/proxmox/labs/lab_one/install-lab-elements.sh"]
    only=["proxmox-iso.lab_one_node_42","proxmox-iso.lab_one_node_41"]
  }

}
