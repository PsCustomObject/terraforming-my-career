---
title: "02 Ec2 Instances"
nav_exclude: true
---

# EC2 Instances — Final Version

## 🧭 First Step – Set up a Budget

💰 Before experimenting with EC2 (one of the oldest AWS services), create a **training budget** so you can track or stop unexpected spend.

1. Log in as the **root user**. Budgets and the Billing Dashboard are hidden from IAM users until the root user enables access.
2. Open **Billing & Cost Management → Account Settings**.
3. In **IAM user and role access to Billing information**, enable access for IAM identities.
4. Create a budget (often a **Zero-Spend Budget** when studying). Use the wizard or define custom thresholds and alerts.

---

## 🖥️ EC2 Overview

**Elastic Compute Cloud (EC2)** is AWS’s *Infrastructure as a Service (IaaS)* offering, allowing you to deploy and manage virtual machines.

As with any IaaS, **you** are responsible for:

- OS-level security  
- Updates & patching  
- Installed applications  
- Instance configuration  

EC2 virtual machines — called **instances** — are built from **Amazon Machine Images (AMIs)**.

### Core EC2 capabilities

- 🔄 **Auto Scaling Groups (ASG)** — scale capacity based on demand  
- 📦 **EBS** or **EFS** — attach persistent storage  
- ⚖️ **Elastic Load Balancers (ELB)** — distribute traffic across instances  

> 🎯 **Exam Alert:** EC2 = IaaS → *You manage the OS, software, patches & networking*.

---

## ⚙️ Instance Types

An **instance type** defines CPU, RAM, network performance, and storage options.

Free Tier instances include **t2.micro** and **t3.micro**.

AWS provides a **Compare Instance Types** tool in the console.

### 📚 Instance Families (Summary)

| Family                            | Optimized For            | Examples                   |
|-----------------------------------|--------------------------|----------------------------|
| 🧩 **General Purpose (t, m)**     | Balanced workloads       | Web servers, small apps    |
| ⚡ **Compute Optimized (c)**       | CPU-bound tasks          | Batch jobs, media encoding |
| 🧠 **Memory Optimized (r, x, z)** | Large in-memory datasets | Databases, caching         |
| 📦 **Storage Optimized (i, d)**   | High IOPS / throughput   | OLTP, NoSQL, warehousing   |
| 🎮 **Accelerated (p, g, inf)**    | GPU & ML workloads       | AI/ML, HPC                 |
| 🚀 **HPC (hpc)**                  | Tightly coupled HPC      | Scientific computing       |

### 🔤 Instance Naming Convention

Example: **m4.2xlarge**

- **m** → instance family  
- **4** → generation  
- **2xlarge** → size (CPU/RAM scaling)

---

## 🔑 Key Pair (Login)

Linux instances use SSH key pairs.

AWS allows:

- generating a key pair  
- uploading your own public SSH key  

You can download the private key (`.pem`) only once during instance creation. Of course public keys already in our possess or created for other instances can be used despite the latter is not considered a best practice.

---

## 🌐 Network Settings

Instances receives a **Public IP** automatically.

Access is controlled by **Security Groups**.

AWS may auto-create an SG rule for SSH access when launching Linux.

> ⚠️ **Important:** Public IPs assigned at launch are *dynamic*.  
Stopping & starting an instance assigns a new IP unless using an **Elastic IP**.
> 💡 **Elastic IPs** are static public IPs allocated to your account and attached manually to an instance.

---

## 📦 Storage

EC2 creates an **EBS root volume** by default.  
This means the OS disk persists when the instance is stopped.

In *Advanced* settings you can choose whether the volume should:

- Persist  
- Be deleted on termination (default: **deleted**)  

> 🧠 **Instance Lifecycle Summary**
>
> - Stop: EBS volume persists  
> - Terminate: EBS may be deleted (based on flag)  
> - Instance Store: always lost on stop/terminate  

---

## 🧰 User Data

**User Data** lets you run a script **only on first boot**.

Common uses:

- Installing software  
- Bootstrapping environment  
- Updating packages  

Heavy scripts = slower instance initialization.

---

## 🛡️ Security Groups (EC2 Firewall)

Security Groups are **stateful firewalls**.

- 🚫 **Inbound** = denied by default  
- ✅ **Outbound** = allowed by default  
- 🔁 Return traffic is automatically allowed  

Security Group rules specify:

- Rule type (SSH, HTTP, etc.)
- Protocol
- Port or range
- Source (IP or Security Group)
- Description

Security Groups can also **reference other SGs**, enabling multi-tier architectures.

> 💡 **Best practice:** Create a dedicated SSH SG per server or role.

---

## 🐧 SSH Access (Linux)

EC2 Linux instances use SSH key authentication.  
The default user varies by AMI (e.g., `ec2-user` for Amazon Linux).

### 🔧 Permissions Issue (macOS / Linux)

Private keys must not be world-readable.

Fix with:

```bash
chmod 600 my-key.pem
```

---

## 🛰️ EC2 Instance Connect

Browser-based SSH access using **temporary keys**.

Security Group rules **still apply**.  
If port 22 is closed → access denied.

---

## 🎟️ EC2 Roles

IAM Roles allow EC2 instances to access AWS services **without storing credentials**.

Common uses:

- Access S3 buckets  
- Access DynamoDB  
- Access SQS, SNS  
- Secure in-instance AWS CLI usage  

---

## 💵 EC2 Purchasing Options

AWS offers cost models for different workload patterns.

### ⏱️ On-Demand

- Pay by second (Linux) or hour (Windows/macOS)  
- No commitment  
- Highest cost  
- Best for **short-lived or unpredictable** workloads

### 💰 Reserved Instances (1 or 3 years)

- Significant discount scaling with **Payment method** (see below) and time committment (1 or 3 years)
- Flexible payment (**No Upfront**, **Partial**, **All Upfront**)  
- Convertible RIs **allow** changing instance *family/OS/tenancy*
- Can be sold on RI Marketplace  
- Ideal for **steady, long-running** workloads  

### 💳 Savings Plans

- Commit to a **$ per hour** for 1 or 3 years  
- More flexible than RIs  
- Still tied to region and family (instances cannot be modified)

### 🪙 Spot Instances

- Up to **90% discount**  
- Can be terminated when AWS needs capacity  
- Great for **intermittent or fault-tolerant** workloads like:
  - Images editing
  - Batch Jobs
  - Disributed computing

### 🏢 Dedicated Hosts

- Entire physical server allocated to you  
- Required for licensing tied to sockets/cores  
- Highest-cost option  

### 🔒 Dedicated Instances

- Hardware not shared with other customers  
- No instance placement control  

### 📌 Capacity Reservations

- Reserve capacity in a specific AZ  
- Billed On-Demand even if unused  
- Ensures availability for critical workloads  

---

## 🛡️ Shared Responsibility Model (EC2)

### **AWS Responsibilities**

- Global infrastructure security  
- Physical hardware  
- Networking and hypervisor  
- Faulty hardware replacement  
- Cloud platform compliance  

### **Your Responsibilities**

- OS patching  
- Application security  
- IAM roles & access  
- Security Group rules  
- Data encryption & backup  

---

## 🧠 Common EC2 Exam Questions

| Question                                             | Answer             |
|------------------------------------------------------|--------------------|
| Which model offers lowest cost for short-term jobs?  | Spot               |
| When does user data run?                             | On first boot only |
| Are Security Groups stateful?                        | Yes                |
| What happens to EBS on stop?                         | Persists           |
| What happens to Instance Store on stop/terminate?    | Lost               |
| Which model provides highest flexibility + discount? | Savings Plans      |

---

## 📘 Summary

## 📘 Summary — EC2 Essentials

- **EC2 (Elastic Compute Cloud)** is AWS’s IaaS service for deploying and managing virtual machines.
- You control the **OS**, **networking**, **software**, **updates**, and **security configuration**.
- Instances are launched from **AMIs** and come in different **families** optimized for compute, memory, storage, or GPU.
- **Security Groups** act as stateful firewalls. Inbound = denied by default, outbound = allowed.
- **Key Pairs** are used for SSH access (Linux). Store `.pem` files securely.
- **User Data** runs once at first boot — ideal for bootstrap scripts.
- Use **IAM Roles** instead of access keys for secure access to AWS services.
- Choose the right **pricing model**:
  - **On-Demand** for flexibility
  - **Reserved** or **Savings Plans** for steady workloads
  - **Spot** for cost-effective, interruptible tasks
  - **Dedicated** for regulatory/licensing needs
- **Elastic IPs** provide static public IPs if needed across reboots.
- **Storage** is usually EBS (persists when stopped). **Instance Store** is ephemeral.
- **Instance Lifecycle**:
  - Stop = EBS persists  
  - Terminate = EBS may delete  
  - Instance Store = lost
- **Shared Responsibility**:
  - AWS: infrastructure, hardware, virtualization
  - You: OS, apps, access control, data protection
