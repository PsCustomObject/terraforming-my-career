---
title: 02‑Change‑Management
parent: Terraform
nav_order: 2
---

# 🌀 Change Management with Terraform

## 🎯 Goals

- Understand the full Terraform lifecycle: `plan` → `apply` → `destroy`
- Interpret the symbols (`+`, `~`, `-`) in the `terraform plan` output
- Learn to preview and safely execute infrastructure changes

---

## 🧠 Key Concepts

- **Dry‑run vs. apply**:
  `terraform plan` shows the changes that would occur, without applying them.
  `terraform apply` commits the changes to real infrastructure.

- **Known after apply**:
  Some attributes (like IP addresses or ARNs) are only available after the resource is created. These appear as `"<computed>"` or `"known after apply"` in the plan output.

- **Auto‑approval**:
  `terraform apply -auto-approve` skips interactive confirmation. Use with caution.

---

## 🛠️ Commands & Syntax

```bash
terraform plan                 # Preview changes without applying
terraform apply                # Apply changes interactively
terraform apply -auto-approve  # Apply changes without confirmation
terraform destroy              # Remove all resources defined in the current configuration
```

---

## 🔄 What Happens When Changing an AMI in Terraform

When updating the AMI ID for an EC2 instance in a Terraform configuration, **you don't need to re-run `terraform init`**. That command is only required when:

- Adding new providers or modules
- Changing backends
- Performing first-time setup in a new directory

To apply a change like an updated AMI, simply run:

```bash
terraform apply
```

---

### ⚙️ How Terraform Handles the Change

Terraform knows that **some changes cannot be applied in-place**. Updating the AMI is one of these — EC2 instances can't be modified to use a new AMI directly. Instead, Terraform plans to:

1. **Destroy** the existing EC2 instance
2. **Create** a new EC2 instance with the updated AMI

In the output of `terraform plan`, this is indicated by a `~` (update) symbol, but more importantly, you'll see a **destroy-and-recreate** operation due to the `forces replacement` marker:

```hcl
# aws_instance.app_server must be replaced
-/+ resource "aws_instance" "app_server" {
    ~ ami = "ami-830c94e3" -> "ami-08d70e59c07c61a3a" # forces replacement
    ...
}
```

Terraform will ask for confirmation before proceeding with any change and will clearly indicate what attribute(s) are triggering the replacement (in this case, the `ami` change).

> 💡 It's best practice to version-control your `.tf` files and always review the `terraform plan` output carefully to understand the implications of changes.

---

## 📚 Further Reading

- [Terraform Plan Command](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Terraform Apply Command](https://developer.hashicorp.com/terraform/cli/commands/apply)
- [Terraform Destroy Command](https://developer.hashicorp.com/terraform/cli/commands/destroy)
- [How Terraform Plan Works Internally](https://developer.hashicorp.com/terraform/internals/plan)
