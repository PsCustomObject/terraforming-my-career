---
title: "00 Cloud Essentials"
nav_exclude: true
---

# ☁️ Cloud Essentials Overview

---

## 🌐 Cloud Delivery Models

Cloud deployment models can be grouped into **three** main service types:

### 🖥️ On-Premises (Traditional)

Everything is hosted in your own data center. You are responsible for:

- Physical servers
- Networking and firewalls
- Storage (disks, SANs)
- Virtualization layer
- Operating systems
- Middleware and applications

All hardware and software must be maintained, patched, and secured manually.

---

### 🏗️ IaaS – Infrastructure as a Service

In **IaaS**, the cloud provider manages:

- Physical servers
- Storage hardware
- Networking
- Virtualization

You manage:

- Operating systems
- Runtime environments
- Databases
- Application logic
- Security (at the OS/app level)

📌 **Examples:** EC2, S3, VPC, EBS

---

### 🧱 PaaS – Platform as a Service

In **PaaS**, the provider handles everything *except* the application code and data. You manage:

- Your application logic
- The data it needs

📌 **Examples:** AWS Elastic Beanstalk, Heroku, Google App Engine

---

### 💻 SaaS – Software as a Service

In **SaaS**, the provider manages everything — you simply use the product.

📌 **Examples:** Gmail, Dropbox, Salesforce, Microsoft 365

---

## 🌍 AWS Global Infrastructure

**Amazon Web Services (AWS)** offers a highly available and redundant infrastructure built on three core components:

### 🗺️ Regions

A **region** is a geographical area (e.g., `eu-west-2` = London). Each region contains **multiple Availability Zones (AZs)** and is isolated from other regions for fault tolerance and compliance.

- AWS has 30+ regions globally
- **Service availability and pricing vary by region**

---

### 🧩 Availability Zones (AZs)

An AZ is **one or more data centers** with independent power, cooling, and networking. They are:

- Physically separated
- Connected by **high-speed, low-latency private fiber**
- Typically 3 to 6 AZs per region

> ✅ Best practice: Deploy workloads across **multiple AZs** for high availability

---

### 🚦 Points of Presence (PoPs) / Edge Locations

AWS maintains **over 400 Edge Locations** and **regional caches** to serve content faster, closer to the user.

- Used by services like **CloudFront** and **Route 53**
- Improve **latency, performance**, and **content delivery**
- You can serve content globally without deploying infrastructure in every country

---

> 🧭 **Note:**  
> This overview introduces core cloud models and AWS infrastructure components.  
> More complex AWS services and architectural stacks (e.g., EC2, IAM, S3, VPC, Lambda, Route 53, etc.)  
> will be explored in detail in later modules as part of this hands-on journey.
