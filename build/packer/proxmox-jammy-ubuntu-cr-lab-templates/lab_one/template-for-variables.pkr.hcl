//  variables.pkr.hcl

// For those variables that you don't provide a default for, you must
// set them from the command line, a var-file, or the environment.

# This is the name of the node in the Cloud Cluster where to deploy the virtual instances
locals {
  NODENAME1 = vault("/secret/data/NODENAME","NODENAME1")
}

locals {
  NODENAME2 = vault("/secret/data/NODENAME","NODENAME2")
}

locals {
  NODENAME3 = vault("/secret/data/NODENAME","NODENAME3")
}

locals {
  NODENAME4 = vault("/secret/data/NODENAME","NODENAME4")
}

locals {
  USERNAME = vault("/secret/data/ACCESSKEY","PK-USERNAME")
}

locals {
  PROXMOX_TOKEN = vault("/secret/data/SECRETKEY","PK-TOKEN")
}

locals {
  URL = vault("/secret/data/URL","NODE1")
}

locals {
  SSHPW = vault("/secret/data/SSH","SSHPW")
}

locals {
  SSHUSER = vault("/secret/data/SSH","SSHUSER")
}

##############################################################################
# This set of variables controls the resources allocated to building the 
# VM templates -- the resources can be low because we will expand/declare the
# resources we want when we deploy instances from these templates via Terraform
###############################################################################
variable "MEMORY" {
  type    = string
  default = "8192"
}

# Best to keep this low -- you can expand the size of a disk when deploying 
# instances from templates - but not reduce the disk size -- No need to edit this
variable "DISKSIZE" {
  type    = string
  default = "10G"
}

# This is the name of the disk the build template will be stored on in the 
# Proxmox cloud -- No need to edit this
variable "STORAGEPOOL" {
  type    = string
  default = "templatedisk"
}

variable "NUMBEROFCORES" {
  type    = string
  default = "1"
}

# This is the name of the Virtual Machine Template you want to create
variable "VMNAME" {
  type    = string
  default = "lab-one-edge-server-template"
}

# This is the name of the Virtual Machine Template you want to create
variable "LN-VMNAME" {
  type    = string
  default = "lab-one-node-template"
}

variable "iso_checksum" {
  type    = string
  default = "file:https://mirrors.edge.kernel.org/ubuntu-releases/22.04.5/SHA256SUMS"
}

variable "iso_urls" {
  type    = list(string)
  default = ["http://mirrors.edge.kernel.org/ubuntu-releases/22.04.5/ubuntu-22.04.5-live-server-amd64.iso"]
}

variable "local_iso_name" {
  type    = string
  default = "ubuntu-22.04.5-live-server-amd64.iso"
}

variable "TAGS" {
  type = string
  default  = "lab_one;cr"
}

# This is the IP address that the Packer HTTP server will bind to when serving the autoinstall config to the VM during the build process
variable "BIND_ADDRESS" {
  type    = string
  default = "10.110.0.98"
}