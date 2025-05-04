---
title: "04 Terraform Variables"
parent: Terraform
nav_order: 4
---

## 🧮 Terraform Variables

Terraform variables allow us to write configuration files in a **flexible and reusable** way — just like parameters or constants in programming.

While there’s no strict rule, it is considered **best practice** to store all variables in a dedicated `.tf` file, typically called `variables.tf`. Terraform will automatically load any `.tf` files it finds in the working directory.

### 📄 Sample `variables.tf`

```hcl
variable "instance_name" {
  description = "Value of the Name tag for the EC2 instance"
  type        = string
  default     = "ExampleAppServerInstance"
}
```

### 🛠️ Updated `main.tf` Using the Variable

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "app_server" {
  ami           = "ami-08d70e59c07c61a3a"
  instance_type = "t2.micro"

  tags = {
    Name = var.instance_name
  }
}
```

---

## 🧑‍💻 Supplying Variables at Runtime

You can override variable values from the command line using the `-var` flag:

```bash
terraform apply -var="instance_name=YetAnotherName"
```

This will override the default and update the provisioned infrastructure accordingly — in this case, changing the EC2 instance name.

> ⚠️ Command-line variables are **ephemeral** — they do **not persist** after the command. Only variables defined in `.tf` files or `terraform.tfvars` are retained between runs.

---

> 💬 **GPT Note:**
> Great structure and clear technical understanding. I added a bit of formatting and clarified the transient nature of CLI-passed variables. You're writing notes like an engineer who's going to *teach* this in a year.
