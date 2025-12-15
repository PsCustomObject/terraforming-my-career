---
title: "03 EC2 Instance Storage"
nav_exclude: true
---


# 🧠 EC2 Instance Storage – Notes & Concepts

## 🧱 EBS Overview

**EBS** stands for **Elastic Block Storage**.  
It provides **persistent block-level storage volumes** for EC2 instances.

- EBS volumes **persist even after instance termination**, depending on configuration
- They are **bound to a single Availability Zone (AZ)** and **cannot be attached across AZs**
- EBS volumes are **network-attached** drives, not physically connected
- Volumes can be **detached and reattached** to other instances within the same AZ
- To move across AZs, take a **snapshot**, then create a new volume in another AZ

EBS volumes can be provisioned for:

- Size (in GB)
- Performance (IOPS)

Both can be modified over time.

> ✅ **Note for the Practitioner exam:** EBS is single-attach by default (one volume ↔ one instance), even though multi-attach exists.

### 📌 Delete on Termination

- By default, the **root volume** has “Delete on Termination” **enabled**
- Other volumes do **not**, and will persist unless explicitly deleted
- This behavior is configurable at instance launch

> 🔒 Changing the root volume's termination behavior **cannot be done via the Console** once launched — use CLI or PowerShell.

## 🗂️ EBS Snapshots

- **Snapshots** are backups of EBS volumes
- They can be created **while the volume is in use**, though consistency is not guaranteed
- Snapshots are stored in S3 (but not directly accessible via the S3 console)

### 🔁 Snapshot Archiving

- Snapshots can be archived to **EBS Snapshot Archive**  
  🏷️ 75% cheaper, but takes 24–72h to restore

- Snapshots can also be sent to a **Recycle Bin** with retention from 1 to 365 days

- Volumes can be recreated from snapshots in **any AZ**

## 📦 Amazon Machine Image (AMI)

**AMI = Amazon Machine Image**, a **template** for launching EC2 instances.  
Similar in concept to **VMware templates**.

- An AMI is region-specific but **can be copied across regions**
- An AMI includes: OS + configuration + installed packages + metadata

### 🛠️ Creating a Custom AMI

1. Launch and configure an EC2 instance
2. Stop the instance (for consistency)
3. Create the AMI (snapshot-based)
4. Launch new instances from that AMI

## 🧪 EC2 Image Builder

**EC2 Image Builder** automates the creation, testing, and distribution of AMIs.

### 🔄 Flow

1. EC2 Image Builder creates a temporary **Builder Instance**
2. Customizations (updates, packages) are applied
3. AMI is created
4. Optional **tests are run automatically** (security, health, etc.)
5. AMI is distributed to chosen regions

- Can run **manually, on schedule, or triggered by events**
- Image Builder is **free** — you pay only for underlying EC2, storage, and data transfer

## ⚡ EC2 Instance Store

An **EC2 Instance Store** is a type of **ephemeral storage** that offers:

- Very fast **physical disks** attached to the host machine
- Better performance than EBS, but **non-persistent**

> ❗ If the instance is stopped or terminated, **all data is lost**

### 🧰 Best Use Cases

- Scratch data
- Temporary cache
- Buffering
- Data that can be rebuilt or is disposable

> 🛑 Not suitable for databases or data that must survive stop/terminate

## 📁 EFS Overview

**EFS = Elastic File System**  
A **fully-managed, scalable, NFS-based shared file system**.

- Can be mounted by **hundreds of EC2 instances simultaneously**
- Works **across AZs**
- **Linux-only** (not compatible with Windows)
- **Pay-per-use**, no capacity planning required

### 🧊 EFS-IA (Infrequent Access)

- For rarely accessed files
- Costs up to **92% less**
- EFS can auto-move files to EFS-IA based on **Lifecycle Policies**

## 🛡️ Shared Responsibility Model (Storage)

| **AWS Responsibility**                         | **Customer Responsibility**                         |
|------------------------------------------------|-----------------------------------------------------|
| Underlying infrastructure                      | Managing backups/snapshots                          |
| Hardware replacement, AZ replication (EBS/EFS) | Data encryption                                     |
| Isolation from AWS personnel                   | Managing access controls                            |
| Availability guarantees                        | Choosing persistence model (EBS vs. Instance Store) |

> ❗ For **Instance Store**, customers are fully responsible for data survival

## 📡 Amazon FSx Overview

**Amazon FSx** provides **managed third-party file systems**.

- **FSx for Lustre** – HPC, parallel workloads
- **FSx for Windows File Server** – Full SMB support, Windows-native
- **FSx for NetApp ONTAP** – Advanced storage with NetApp features

## ✅ Quick Summary (Cheat Sheet Style)

| **Storage Type**   | **Persistent** | **Attachable to Multiple EC2s** | **Use Case**                              |
|--------------------|----------------|---------------------------------|-------------------------------------------|
| **EBS**            | Yes            | No (by default)                 | General-purpose block storage             |
| **Instance Store** | No             | No                              | High-speed, temporary scratch space       |
| **EFS**            | Yes            | Yes (Linux only)                | Shared file systems, scaling workloads    |
| **FSx**            | Yes            | Yes (depends on config)         | Windows/NetApp/Lustre high-performance FS |
