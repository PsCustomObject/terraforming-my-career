---
title: Macro Plan
parent: Meta
nav_order: 2
---

# 🗺️ Terraforming My Career – Macro Plan

> A sequential roadmap to become Cloud & Platform Engineer with Terraform, AWS, Docker, Kubernetes & Observability

---

## 🌱 Phase 0 – Orientation & Setup

- [x] Install AWS CLI, Git, and Terraform
- [x] Create and test programmatic access to AWS (Free Tier)
- [x] Create repo structure & initial notes (`terraforming-my-career`)
- [x] Write `01-getting-started.md`
- [x] Complete `02-change-management.md`
- [x] Complete `03-destroy-infrastructure.md`
- [x] Start reading *Terraform Up & Running* (Third Edition)
- [ ] Maintain reading notes in `terraform-up-and-running.md`

---

## 🧱 Phase 1 – Core Terraform Fundamentals

- [ ] 📘 Finish Chapter 2 of the book
- [x] Create `04-variables-outputs.md`
- [ ] Practice defining variables and outputs
- [ ] Use `.tfvars` and CLI vars
- [ ] Practice writing clean, parameterized `.tf` configs
- [ ] Extend with conditional logic and interpolation

---

## 🧰 Phase 2 – Modules & Reusability

- [ ] 📘 Read Chapter 6 (Terraform Up & Running)
- [ ] Create `05-modules.md`
- [ ] Refactor EC2 & S3 configs into modules
- [ ] Learn `source`, `input`, `output`, `locals`
- [ ] Create your own root and child module structure

---

## 🌐 Phase 3 – Remote State & Workspaces

- [ ] 📘 Read Chapter 7
- [ ] Create `06-remote-state.md`
- [ ] Store Terraform state in S3
- [ ] Use DynamoDB for state locking
- [ ] Configure multiple workspaces (dev/staging/prod)

---

## 🛡️ Phase 4 – Validation & Testing

- [ ] Integrate `terraform validate`, `fmt`, `plan`
- [ ] Learn `tflint`, `tfsec`, `checkov`
- [ ] Create `07-validation.md` with examples
- [ ] Automate checks with Makefile or GitHub Actions

---

## 🐳 Phase 5 – Docker Fundamentals

- [ ] Create `docker/01-getting-started.md`
- [ ] Build custom images (single & multi-stage)
- [ ] Push to Docker Hub or ECR
- [ ] Learn `docker-compose`

---

## 🔄 Phase 6 – CI/CD with GitHub Actions

- [ ] Automate Terraform plan/apply (non-prod)
- [ ] Set up basic pipeline for Docker builds
- [ ] Trigger Terraform via PRs or commits

---

## ☸️ Phase 7 – Kubernetes Fundamentals

- [ ] Set up Minikube or K3s locally
- [ ] Deploy simple apps with manifests
- [ ] Use Helm charts
- [ ] Create `kubernetes/intro.md`

---

## 🔍 Phase 8 – Observability & Platform Thinking

- [ ] Deploy Prometheus + Grafana + Loki
- [ ] Instrument simple metrics/logs
- [ ] Create dashboards for EC2 or K8s
- [ ] Reflect on platform-as-product mindset

---

## 🔚 Ongoing & Capstone Ideas

- [ ] Track jobs and reflect in `meta/job-search.md`
- [ ] Design a sample multi-env platform from scratch
- [ ] Write blog posts or project README with architecture diagrams
