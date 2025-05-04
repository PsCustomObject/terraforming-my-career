---
title: Chapter 01 Intro
parent: Reading-Notes
nav_order: 1
---

# 🧱 Chapter 1 – Why Terraform and DevOps

**DevOps** enables faster, more reliable application delivery by promoting automation, repeatability, and collaboration. The classic *“it worked on my machine”* problem is mitigated by making both code and infrastructure reproducible.

As infrastructure shifts from physical hardware to cloud-based services, the boundary between “Dev” (developers) and “Ops” (operations/system administrators) is blurring. This is where **Infrastructure as Code (IaC)** steps in.

IaC is the practice of writing and executing code to **define**, **deploy**, **update**, and **destroy** infrastructure — aligning perfectly with DevOps principles, especially:

- Everything is code
- Everything can be versioned, validated, and automated

### ✅ Benefits of IaC

- **Declarative:** Focus on *what* you want, not *how* to do it
- **Versionable:** Stored in Git or other VCS, with commit history
- **Reproducible:** Same result every time = **idempotency**
- **Self-Service:** Developers can deploy infrastructure independently
- **Speed & Safety:** Automated steps reduce human error and increase delivery velocity
- **Documentation by Design:** The code *is* the documentation, eliminating the “black box” effect
- **Change Control & Auditing:** Commit logs show who changed what and when
- **Validation:** Changes can go through CI pipelines with tests before being applied
- **Reusability:** Infrastructure can be abstracted into reusable modules (think classes/functions)

---

## ⚙️ How Terraform Works

Terraform is a single static binary written in Go. It can be executed on any machine (local, CI server, etc.) with zero external dependencies.

Terraform uses **providers** (e.g., AWS, Azure, GCP) to interact with cloud APIs. These providers define the types of resources you can create and how to communicate with each platform.

> 🧠 Terraform doesn’t manage infrastructure itself — it orchestrates **API calls** to platforms that already do.

The **Terraform configuration** is a collection of `.tf` text files that define desired infrastructure. These files are parsed and executed by the Terraform binary.

Typical workflow:

```bash
terraform init   # Downloads required provider plugins
terraform plan   # Shows what changes will happen
terraform apply  # Applies changes via API calls
```

When an update is needed (e.g., change instance type), you **change the code**, commit the changes, and re-apply. Terraform detects the delta and executes only the necessary API operations.

---

## 🔄 Mutable vs Immutable Infrastructure

Traditional tools like Ansible operate in a **mutable** model: they log into existing servers and mutate their state (e.g., upgrade OpenSSL in-place). Over time, these systems diverge, even if they started identically.

In contrast, **immutable infrastructure** replaces systems instead of modifying them. Example:

- A new AMI is built with Packer and the updated OpenSSL version
- Terraform replaces existing EC2 instances with new ones
- Old instances are destroyed

Benefits:

- Prevents drift between environments (e.g., test vs prod)
- Promotes predictability and reproducibility
- Simplifies rollback — just deploy a previously built image
- Improves test coverage — if it passed CI, it’ll behave the same in production

> 💡 Terraform defaults to **immutable infrastructure** by design.

---

## 🛠️ Chapter 2 – Building Infrastructure

- [ ] Core components:
  - Providers → Resources → State
- First resource: `aws_instance`
- Terraform workflow:
  - `init`, `plan`, `apply`, `destroy`

---

## 🔄 Chapter 3 – Updating Infrastructure

- [ ] Immutable infra mindset: replace > mutate
- AMI changes = destroy & recreate (forces replacement)
- Importance of planning before applying

---

## 🧠 Concepts to Revisit

- [ ] Tainting
- [ ] Resource lifecycle
- [ ] Remote state & locking
