# Terraform: Getting Started

## Key Concepts

- **Declarative**: define _what_ you want, not _how_ to do it
- **Providers**: AWS, Azure, etc.
- **Resources**: actual infra components (e.g., `aws_instance`)
- **State**: Terraform tracks what it manages via `terraform.tfstate`

## Terraform State

Terraform uses a **state file** (`terraform.tfstate`) to keep track of the real infrastructure it manages. This file records the current state of all resources created, updated, or destroyed by Terraform, allowing it to determine what actions are required during future operations.

The state file can contain sensitive data (e.g., passwords, secrets, or cloud resource metadata). For this reason, it should be stored securely with access strictly controlled — for example, in an encrypted S3 bucket with restricted permissions, accessible only to team members responsible for infrastructure management.

The current state can be inspected using the `terraform show` command. This displays all information that Terraform has about the infrastructure, including metadata returned by the provider for each resource (e.g., EC2 instance details, IP addresses, or ARNs).

Terraform **creates a single backup** of the previous state file (**terraform.tfstate.backup**) *before modifying the current state*. This allows a rollback to the immediately prior state version if needed, but it does not store a full version history.

> 💡 Using a remote backend like AWS S3 with versioning enabled allows **every** past version of the state file to be preserved. This enables recovery of any previous state using S3's versioning interface or API.

## Key Commands

```bash
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
terraform destroy
terraform show
terraform refresh # optional and probably obsolete
```

## Key commands reference

### terraform init

`terraform init` initializes a Terraform working directory. It downloads the necessary **provider plugins**, sets up the backend (if configured), and prepares the directory for future commands such as `plan` and `apply`.

**This command must be run before executing any other Terraform operation within a new or freshly cloned project**. It can also be used to reinitialize a project if providers or backend settings have changed.

> 💡 Without running `terraform init`, Terraform commands such as `plan` or `apply` will not function, as required dependencies and configurations are not yet available.

### terraform fmt

`terraform fmt` formats Terraform configuration files to a canonical style. This command ensures consistent indentation and alignment across `.tf` files in a project.

Although optional, it is useful for maintaining readability and standardization. Most modern editors, such as Visual Studio Code, can handle formatting automatically through plugins or built-in support.

> 💡 `terraform fmt` **modifies files in place** unless used with the `-check` or `-diff` flags.

### terraform validate

`terraform validate` checks the syntax and internal consistency of Terraform configuration files. It verifies that the **configuration is syntactically valid** and that referenced resources, variables, and providers are correctly defined.

This command does not interact with remote services or check resource availability. It is often used in local development or CI pipelines to catch errors before planning or applying changes.

> 💡 Editors like Visual Studio Code may catch syntax errors in real time, but `terraform validate` provides a more complete structural validation.

### terraform plan

`terraform plan` performs a dry run of the execution process. It compares the desired state defined in the Terraform configuration files with the current state of the infrastructure (as tracked in the state file and/or by querying the provider).

The output indicates what actions Terraform _would_ take to reconcile differences between the configuration and actual infrastructure, without performing any changes.

- `+` **Created**
- `~` **Modified**
- `-` **Destroyed**

This command is used to preview changes and verify that the configuration behaves as expected before applying any updates to the infrastructure.

> 💡 `terraform plan` acts as a safety step, allowing verification and review before execution.

### terraform apply

`terraform apply` is the command that actually makes changes to the infrastructure, based on the Terraform configuration (e.g., `main.tf`).

Before applying any change, Terraform shows a plan-like output summarizing what will be:

- `+` **Created**
- `~` **Modified**
- `-` **Destroyed**

Changes must be **manually confirmed** (unless using `-auto-approve`) before anything is executed.

Fields marked as `"known after apply"` indicate attributes that will only be available _after_ the resource is created — such as resource IDs, ARNs, or dynamically assigned IP addresses returned by the provider.

> 💡 Think of `terraform plan` as a dry-run preview, and `terraform apply` as the "**commit & push**" to the cloud.

### terraform destroy

`terraform destroy` is used to terminate all resources tracked in the current Terraform state. It removes the infrastructure defined in the configuration files by issuing corresponding delete commands to the cloud provider.

If a resource has already been manually deleted outside of Terraform (e.g., via the AWS Console or CLI), Terraform will detect that it no longer exists and will take no action on it during the destroy process.

> 💡 This command should be used with caution, as it will remove all managed infrastructure unless specific targets are defined.

### terraform refresh

`terraform refresh` updates the Terraform state file to match the real-world state of the infrastructure by querying the provider for the current status of all managed resources.

This command is useful when infrastructure has been modified outside of Terraform (e.g., manually deleted or changed via the console) and the state file needs to be updated accordingly.

In most workflows, `terraform plan`, `apply`, and `destroy` automatically perform a refresh. Manual use of `terraform refresh` is typically reserved for troubleshooting or resolving drift.

> 💡 `terraform refresh` does not modify resources; it only updates the state file with the latest information from the provider.
