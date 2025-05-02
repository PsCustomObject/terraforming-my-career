---
title: Learning Plan
parent: Meta
nav_order: 1
---

# Cloud & Platform Engineering Learning Plan 🚀

**Start Date:** April 29, 2025
**Goal:** Transition into a Cloud & Platform Engineering role by mastering Terraform, AWS, Docker, Kubernetes, and modern DevOps practices through hands-on labs and documentation.

---

## 🧭 Timeline Overview

| Week | Dates            | Phase     | Focus Topic                        |
|------|------------------|-----------|------------------------------------|
| 1    | Apr 29 – May 5   | Phase 0   | Setup & Orientation                |
| 2–5  | May 6 – Jun 2    | Phase 1   | Terraform + AWS Basics             |
| 6–9  | Jun 3 – Jun 30   | Phase 2   | Docker Fundamentals + CI/CD        |
| 10–13| Jul 1 – Jul 28   | Phase 3   | Kubernetes Fundamentals            |
| 14–16| Jul 29 – Aug 18  | Phase 4   | Platform Concepts + Observability  |

---

## ✅ Phase 0 – Setup & Orientation (Week 1)

**Goals:**

- Install and configure Terraform, AWS CLI, and Git
- Setup GitHub repo structure for note-taking
- Read:
  - Terraform AWS Intro Tutorial (EC2 provisioning)
  - Terraform CLI command docs
- Optional:
  - *Terraform Up & Running* (Ch. 1–3)
  - Watch FreeCodeCamp 1-hour intro to Terraform

**Deliverables:**

- Repo: `cloud-notes/terraform/01-getting-started.md`
- AWS CLI authenticated
- GitHub repo synced with initial structure

---

## ⛏️ Phase 1 – Terraform + AWS Basics (Weeks 2–5)

**Goals:**

- Learn Terraform syntax, state, variables, outputs
- Create:
  - EC2 instance
  - S3 bucket
  - IAM user
  - VPC (basic)
- Refresh AWS services via Neal Davis videos as you use them

**Deliverables:**

- Repos:
  - `terraform/ec2-instance`
  - `terraform/s3-module`
- Notes in:
  - `aws/ec2.md`
  - `aws/iam.md`
  - `aws/s3.md`

---

## 🐳 Phase 2 – Docker Fundamentals + CI/CD (Weeks 6–9)

**Goals:**

- Build, tag, and push custom Docker images
- Use `docker-compose` and multi-stage builds
- Automate builds with GitHub Actions or GitLab CI
- Optional: run containers on your home lab

**Deliverables:**

- Repo: `docker/labs` with Dockerfile examples
- GitHub pipeline YAML for image build + push

---

## ☸️ Phase 3 – Kubernetes Fundamentals (Weeks 10–13)

**Goals:**

- Deploy apps to K3s or Minikube
- Learn about Deployments, Services, Ingress, ConfigMaps
- Use Helm to manage templated deployments

**Deliverables:**

- Repo: `kubernetes/labs` with manifests
- Notes in `kubernetes/intro.md`

---

## 🧠 Phase 4 – Platform & Observability (Weeks 14–16)

**Goals:**

- Deploy Prometheus, Grafana, Loki
- Add metrics and logging to your K8s apps
- Understand platform-as-a-product mindset
- Optional: explore GitOps with ArgoCD or Flux

**Deliverables:**

- Monitoring stack deployed in home lab
- `observability.md` with Grafana dashboards or queries

---

## 💡 Tracking Progress

Create a simple checklist in this file or your terminal to track your weekly progress and write reflections.
