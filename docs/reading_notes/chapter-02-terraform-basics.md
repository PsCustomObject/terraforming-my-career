---
title: "Chapter 2 — Terraform Basics"
parent: Reading Notes
nav_order: 2
---

# 🛠️ Chapter 2 – Terraform Basics

## 📁 What to Track in Git

When managing infrastructure with Terraform, it's best practice to commit all configuration (`*.tf`) files to version control — usually Git.

However, Terraform also generates files that should **not** be committed:

```bash
.terraform/
*.tfstate
*.tfstate.backup
```

These files can contain sensitive information such as credentials, private IPs, or internal metadata. They are specific to a local or remote state and **should never be shared or versioned**.

To exclude them, use a `.gitignore` file:

```bash
.terraform/
*.tfstate
*.tfstate.backup
```

> 🔗 Learn more: [Getting started with .gitignore](https://pscustomobject.github.io/git/version-control/getting-started-with-gitignore/)

---

## 🔄 Updating Infrastructure

When you update a Terraform config file and re-apply it, Terraform uses the state file to compare current vs desired infrastructure.

By default, Terraform performs **in-place updates** when possible (e.g., changing an instance type).

However, some changes (like `user_data`) require destroying and recreating the resource. To enforce this behavior explicitly:

```hcl
resource "aws_instance" "example" {
  ami                         = "ami-12345678"
  instance_type               = "t2.micro"
  user_data                   = file("setup.sh")
  user_data_replace_on_change = true
}
```

This ensures a new `user_data` script triggers instance replacement.

> 💡 Use this with care — destruction might cause downtime or loss of ephemeral data.

---

## 🔢 Terraform Expressions

A **Terraform expression** is any snippet of code that returns a value. There are different types:

### ✅ Literals

```hcl
"t2.micro"
true
42
```

### ✅ References (Dynamic)

```hcl
aws_instance.example.public_ip
```

This format is:

```hcl
<provider>_<type>.<resource_name>.<attribute>
```

These references establish **implicit dependencies** — Terraform builds a graph to ensure resources are created in the correct order.

---

## 🧱 Full Example `main.tf` (with ASG)

```hcl
provider "aws" {
  region = "us-east-2"
}

resource "aws_instance" "example" {
  ami                         = "ami-0fb653ca2d3203ac1"
  instance_type               = "t2.micro"
  user_data                   = <<-EOF
    #!/bin/bash
    echo "Hello, World!" > index.html
    nohup busybox httpd -f -p 8080 &
  EOF
  user_data_replace_on_change = true

  vpc_security_group_ids = [
    aws_security_group.allow_http.id,
    aws_security_group.allow_ssh.id
  ]

  tags = {
    Name = "Terraform_Example_Instance"
  }
}

resource "aws_security_group" "allow_http" {
  name        = "allow_http"
  description = "Allow HTTP traffic on port 8080"

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Allow_HTTP"
  }
}

resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh"
  description = "Allow SSH traffic on port 22"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Allow_SSH"
  }
}
```

---

## 🧠 ASG Note

In production, we rarely deploy single EC2 instances directly.

Instead, we use **Auto Scaling Groups (ASGs)** to create, replace, or destroy instances **automatically** behind the scenes. These are usually fronted by a **Load Balancer** (ALB/NLB).

Terraform can still manage individual EC2 instances (useful for labs or prototypes), but for real-world infra, ASG + ALB is the standard pattern.

---

## 📤 Outputs

Terraform lets you expose useful data after `apply` via **output values**.

Example:

```hcl
output "instance_ip" {
  value = aws_instance.example.public_ip
}
```

After applying:

```bash
Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

Outputs:

instance_ip = "18.223.245.12"
```

This is useful for:

- CI/CD pipelines (consume outputs in scripts)
- Sharing information between modules
- Debugging

> 🔍 Terraform also allows `sensitive = true` to prevent secrets (like passwords) from being displayed in CLI output.

---

## 🔒 Lifecycle Management

Terraform lets you customize how it handles specific resources using the `lifecycle` block.

### Example: Prevent deletion

```hcl
resource "aws_instance" "example" {
  # config...

  lifecycle {
    prevent_destroy = true
  }
}
```

This prevents accidental deletion — even if you run `terraform destroy`.

> ⚠️ You must remove the lifecycle block before Terraform will allow you to destroy that resource.

---

### Additional Lifecycle Settings

- `create_before_destroy = true`: Avoids downtime by provisioning a new resource before destroying the old one.
- `ignore_changes`: Tells Terraform to ignore updates to specific attributes, often used when an external system modifies a resource.

```hcl
lifecycle {
  ignore_changes = [tags["last_updated_by"]]
}
```

---

## 🔍 `terraform show`

The command:

```bash
terraform show
```

Displays the full state of the deployed infrastructure — including IDs, IPs, tags, and metadata.

Useful for:

- Debugging
- Auditing
- Confirming what exists vs what’s in the `.tf` files

You can also use:

```bash
terraform show -json > state.json
```

This dumps machine-readable state data for use in automation or CI pipelines.

---

## 🚀 EC2 Clusters and Lifecycle

In real-world deployments, we rarely create standalone EC2 instances. Instead, we use **Auto Scaling Groups (ASGs)** to manage instance clusters that automatically scale based on demand.

To define an ASG in Terraform, we typically use a **Launch Template** (or the legacy Launch Configuration) to define the instance settings.

> ⚠️ Note: Tags are not defined in the launch template, but **in the ASG itself**.

### 🛠️ Launch Template Example

```hcl
resource "aws_launch_template" "example" {
  name_prefix   = "web-"
  image_id      = "ami-0abc1234"
  instance_type = "t2.micro"

  user_data = <<-EOF
    #!/bin/bash
    echo "Hello from LC" > /var/www/html/index.html
  EOF
}
```

### 🛠️ ASG Example

```hcl
resource "aws_autoscaling_group" "example" {
  name                      = "example-asg"
  min_size                  = 1
  max_size                  = 3
  desired_capacity          = 2
  vpc_zone_identifier       = ["subnet-abc123", "subnet-def456"]
  health_check_type         = "EC2"
  health_check_grace_period = 300
  force_delete              = true

  launch_template {
    id      = aws_launch_template.example.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "terraform-asg-example"
    propagate_at_launch = true
  }

  lifecycle {
    create_before_destroy = true
  }
}
```

---

## ♻️ Why `create_before_destroy`?

**Launch Templates are immutable** — changing one creates a replacement. Since ASGs reference the template, the old one can’t be deleted until the ASG is updated.

Terraform normally deletes first, then creates. But this would fail due to the dependency chain.

Using:

```hcl
lifecycle {
  create_before_destroy = true
}
```

Tells Terraform to reverse the flow: create the new template, update dependencies, then destroy the old one.

This avoids the classic **chicken-and-egg** problem.

---

## 🧮 ASGs and Expressions

When defining an ASG, you must associate it with **subnets** (via `vpc_zone_identifier`).

In the earlier example, the subnets were hardcoded. While acceptable in labs, in production it’s better to dynamically fetch subnet IDs using expressions:

```hcl
data "aws_subnets" "example" {
  filter {
    name   = "tag:Environment"
    values = ["dev"]
  }
}

resource "aws_autoscaling_group" "example" {
  vpc_zone_identifier = data.aws_subnets.example.ids
  ...
}
```

This approach ensures portability and avoids tight coupling with hardcoded values.

---
