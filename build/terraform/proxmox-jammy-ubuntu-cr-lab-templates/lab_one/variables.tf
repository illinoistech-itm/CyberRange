#https://registry.terraform.io/providers/Telmate/proxmox/latest/docs

variable "error_level" {
  default = "debug"
}

variable "pm_log_enable" {}

variable "pm_parallel" {}

variable "pm_timeout" {}

variable "pm_log_file" {}

variable "numberofvms" {}

variable "ln_numberofvms" {}

variable "desc" {}

variable "ln_desc" {}

variable "template_to_clone" {}

variable "ln_template_to_clone" {}

variable "memory" {}

variable "cores" {}

variable "sockets" {}

variable "disk_size" {}

variable "keypath" {}

variable "yourinitials" {}

variable "ln_yourinitials" {}

variable "tags" {}

variable "ln_tags" {}

variable "consul-service-tag-contact-email" {}

variable "additional_wait" {
  default = 30
}

variable "clone_wait" {
  default = 30
}
###############################################################################
# This is the consul dns master -- no need to edit this
###############################################################################
variable "consulip-240-prod-system28" {
  default = "10.110.0.88"
}

variable "consulip-240-student-system41" {
  default = "10.110.0.89"
}

variable "consulip-242-room" {
  default = "10.110.0.90"
}
