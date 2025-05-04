---
title: "01 Getting Started"
parent: Terraform
nav_order: 1
---

# Terraform: Getting Started

## 📚 Table of Contents

- [Key Concepts](#key-concepts)
- [Terraform State](#terraform-state)
- [Everyday Commands](#everyday-commands)
- [Advanced Commands](#advanced-commands)

---

## 🧠 Key Concepts

- **Declarative**: define _what_ you want, not _how_ to do it
- **Providers**: AWS, Azure, etc.
- **Resources**: actual infrastructure components (e.g., `aws_instance`)
- **State**: Terraform tracks what it manages via `terraform.tfstate`

---

## 📂 Terraform State

Terraform uses a **state file** (`terraform.tfstate`) to keep track of the real infrastructure it manages. This file records the current state of all resources created, updated, or destroyed by Terraform, allowing it to determine what actions are required during future operations.

The state **file can contain sensitive data** (e.g., passwords, secrets, or cloud resource metadata). For this reason, it should be *stored securely* with access strictly controlled — for example, in an encrypted S3 bucket with restricted permissions, accessible only to team members responsible for infrastructure management.

The current state can be inspected using the `terraform show` command. This displays all information that Terraform has about the infrastructure, including metadata returned by the provider for each resource (e.g., EC2 instance details, IP addresses, or ARNs).

Terraform **creates a single backup** of the previous state file (`terraform.tfstate.backup`) _before modifying the current state_. This allows a rollback to the immediately prior state version if needed, but it does not store a full version history.

> 💡 Using a remote backend like AWS S3 with versioning enabled allows **every** past version of the state file to be preserved. This enables recovery of any previous state using S3's versioning interface or API.

---

## 💻 Everyday Commands

```bash
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
terraform destroy
terraform show
```

### `terraform init`

Initializes a Terraform working directory. It downloads the necessary **provider plugins**, sets up the backend (if configured), and prepares the directory for future commands such as `plan` and `apply`.

> 💡 Without running `terraform init`, Terraform commands such as `plan` or `apply` will not function, as required dependencies and configurations are not yet available.

> ❗ **Danger:** Running `terraform init` within an empty directory would be like instructing Terraform to destroy the whole infrastructure which nine out of ten is not what we want that is why it will throw a warning.

### `terraform fmt`

Formats Terraform configuration files to a canonical style. This command ensures consistent indentation and alignment across `.tf` files in a project.

> 💡 `terraform fmt` **modifies files in place** unless used with the `-check` or `-diff` flags.

### `terraform validate`

Checks the syntax and internal consistency of Terraform configuration files. It does not interact with remote services.

> 💡 While editors like VS Code may catch syntax errors live, `terraform validate` provides more thorough validation.

### `terraform plan`

Performs a dry run of the execution process. It compares the desired state from the `.tf` files with the current state (tracked in `terraform.tfstate` or by querying the provider).

- `+` **Created**
- `~` **Modified**
- `-` **Destroyed**

> 💡 `terraform plan` acts as a safety step, allowing verification and review before execution.

### `terraform apply`

Applies the planned changes to infrastructure. Terraform shows a summary of what will be created, modified, or destroyed and requires confirmation (unless `-auto-approve` is used).

Fields marked as `"known after apply"` indicate attributes that will only be available _after_ the resource is created.

> 💡 Think of `terraform plan` as a dry-run, and `terraform apply` as the "**commit & push**" to the cloud.

### `terraform destroy`

Terminates all resources tracked in the current Terraform state. Use with caution.

> 💡 If a resource has already been manually deleted, Terraform will detect that it no longer exists and skip deletion.

---

## 🛠️ Advanced Commands

```bash
terraform refresh
terraform state list
terraform state show <resource>
terraform state rm <resource>
terraform import
terraform taint
```

### `terraform refresh`

Updates the Terraform state file to match the real-world infrastructure. Useful when infrastructure has been modified outside of Terraform.

> 💡 In most workflows, `plan`, `apply`, and `destroy` already include an automatic refresh making the command _obsolete_ and anyhow a tool to use in very speciic cases.

### `terraform import`

Enables Terraform to begin managing existing infrastructure that was created outside of Terraform.

#### 🧠 Example Use Case

An S3 bucket was created manually via the AWS Console and must now be brought under Terraform management.

```bash
terraform import aws_s3_bucket.my_bucket my-bucket-name
```

> 💡 After importing, it is recommended to run terraform plan to confirm the state matches the configuration.

### `terraform taint`

Marks a specific resource as needing to be destroyed and recreated during the next `terraform apply`, even if the configuration hasn't changed.

#### 🧠 Example Use Case

If you **manually shut down an EC2 instance via the AWS Console**, Terraform won’t detect that as a change — the configuration still matches.

However, if you want to restore that instance to a clean state, you can run:

```bash
terraform taint aws_instance.example
terraform apply
```

> 💡 A taint operation will force terraform to reprovision the resource, EC2 instance in this case, but it will of course get a new _instance id_, IP Address etc.

### `terraform state rm`

Removes a resource from Terraform's state without affecting the real infrastructure.

#### 🧠 Example Use Case

A resource is no longer managed by Terraform (e.g., a CloudWatch alarm), but it should not be destroyed when executing `terraform destroy`.

```bash
terraform state rm aws_cloudwatch_metric_alarm.cpu_alarm
```
