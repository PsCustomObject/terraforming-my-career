---
title: 03 Destroy Infrastructure
parent: Terraform
nav_order: 3
---

# 💣 Destroying Infrastructure with Terraform

## 🎯 Goals

- Understand when and why to use `terraform destroy`
- Learn how Terraform handles dependencies during destruction
- Explore safer alternatives to full teardown

---

## 🧠 Key Concepts

- `terraform destroy` removes **all resources** tracked in the current state file
- Terraform destroys resources in **dependency-aware order**
- Use with caution, especially in production environments

---

## 🛠️ Commands & Syntax

```bash
terraform destroy                 # Interactive prompt
terraform destroy -auto-approve  # No confirmation prompt
terraform plan -destroy          # Preview destruction
terraform destroy -target=<resource>  # Destroy specific resource
```

---

## ⚠️ Risks and Best Practices

- **Destruction is final** unless state and infrastructure are versioned
- Prefer `-target` for surgical deletions when possible
- Always run `terraform plan -destroy` to preview before running full destroy

---

## 🔁 Safer Alternatives

- **Comment out resources** in `.tf` files and run `terraform apply`
- **Split infrastructure** into smaller, modular stacks using workspaces or directories

---

## 🧪 Use Cases

- Cleaning up dev/test environments
- Saving cost during idle periods
- Resetting broken infrastructure to a clean state

## 🧨 terraform destroy – Detailed Description

`terraform destroy` is the opposite of `terraform apply` and, as mentioned earlier, it will terminate **all infrastructure** defined in your `.tf` files and tracked in the state file.

Like with `terraform apply`, Terraform computes an **execution plan**—this time for destruction—automatically determining the correct order based on resource dependencies.

- For a **simple setup** (e.g., a single EC2 instance), Terraform will just terminate the instance.
- In **complex setups** with multiple resources, Terraform will destroy each component in a dependency-aware order (e.g., EC2 instances before subnets, subnets before VPCs, etc.).

> 💡 The execution plan shows which resources will be destroyed and in what order, helping you review before confirming.

### 🔍 Sample Output

```hcl
aws_instance.app_server: Refreshing state... [id=i-0809508b79fdeb452]

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  - destroy

Terraform will perform the following actions:

  # aws_instance.app_server will be destroyed
  - resource "aws_instance" "app_server" {
      - ami                                  = "ami-08d70e59c07c61a3a" -> null
      - arn                                  = "arn:aws:ec2:us-west-2:435557266448:instance/i-0809508b79fdeb452" -> null
      - associate_public_ip_address          = true -> null
      - availability_zone                    = "us-west-2a" -> null
      - cpu_core_count                       = 1 -> null
      - cpu_threads_per_core                 = 1 -> null
      - disable_api_stop                     = false -> null
      - disable_api_termination              = false -> null
      - ebs_optimized                        = false -> null
      - get_password_data                    = false -> null
      - hibernation                          = false -> null
      - id                                   = "i-0809508b79fdeb452" -> null
      - instance_initiated_shutdown_behavior = "stop" -> null
      - instance_state                       = "running" -> null
      ...
```

## ✅ Pro Tip

Instead of using `terraform destroy`, consider removing or commenting out a resource block:

```hcl
# resource "aws_instance" "example" {
#   ami           = "ami-123456"
#   instance_type = "t2.micro"
# }
```

Then run:

```bash
terraform apply
```

Terraform will recognize the resource is no longer in config and safely remove it.

---

## 📚 Further Reading

- [Terraform Destroy Command](https://developer.hashicorp.com/terraform/cli/commands/destroy)
- [Terraform Plan –destroy](https://developer.hashicorp.com/terraform/
