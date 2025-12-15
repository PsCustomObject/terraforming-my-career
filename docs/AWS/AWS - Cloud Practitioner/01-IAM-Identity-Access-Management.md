---
title: "01 IAM Identity Access Management"
nav_exclude: true
---

# Identity and Access Management (IAM)

> 💡 **IAM = Global Service**  
> IAM is a **global** AWS service — it is not region-specific.

IAM is composed of four key components: **Users**, **Groups**, **Policies**, and **Roles**.  
These define *who* can access AWS resources and *how* they can use them.

---

## Users and Groups

A **user** represents an individual identity that can authenticate into AWS services.  
**Groups** organize users together, allowing you to attach permissions (via *policies*) collectively instead of user-by-user.

There are two access methods for users:

- **Console access:** uses a username and password.  
- **Programmatic access:** uses **Access Key ID** and **Secret Access Key** for CLI, SDK, or API access.

A single user can belong to multiple groups, but **groups cannot contain other groups**.

### Root Account

When an AWS account is first created, a **root user** is automatically generated.  
This account has *unrestricted access* and should **only** be used for account setup or billing tasks.  
Immediately enable MFA for the root user and avoid using it for daily operations.

---

## Policies

**Policies** are JSON documents that define *permissions* — what actions are allowed or denied, on which resources, and under which conditions.

### Policy Structure

Each policy includes:

- **Version** — current: `"2012-10-17"`
- **Statement(s)** — one or more permission blocks
  - `Sid` — optional identifier  
  - `Effect` — `"Allow"` or `"Deny"`  
  - `Principal` — who the policy applies to  
  - `Action` — list of actions (e.g., `s3:GetObject`)  
  - `Resource` — target resources (e.g., an S3 bucket)  
  - `Condition` — optional logic for when it applies

Example:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "*",
      "Condition": {
        "DateGreaterThan": {"aws:CurrentTime": "2020-04-01T00:00:00Z"},
        "DateLessThan": {"aws:CurrentTime": "2020-06-30T23:59:59Z"}
      }
    }
  ]
}
```

> 💡 **Tip:** The `"*"` wildcard means “all resources” or “all actions” — use it carefully.

### Policy Types

- **Managed policies:**  
  - *AWS-managed* (prebuilt by AWS)  
  - *Customer-managedß* (you create and maintain them for cases where high customization is required)  
- **Inline policies:** Embedded directly into a *single* user, group, or role.  

**Note:** *Inline policies* should generally be avoided except in very specific, limited-use cases.

### Policy Evaluation Logic

When a user belongs to multiple groups:

- Permissions are the *union* of all attached policies.
- If *any* policy explicitly **denies** an action, the **deny overrides** all allows.
- Actions not explicitly allowed are **implicitly denied**.

> 🧠 **Remember:** *Deny always wins.*  
> If you’re unsure, IAM denies by default.

---

## Multi-Factor Authentication (MFA)

MFA adds a second verification step beyond username and password.

Supported types:

- **Virtual MFA:** e.g., Authy, Microsoft Authenticator, Google Authenticator.  
- **Hardware MFA:** physical tokens such as YubiKeys.

You can assign up to **8 MFA devices per user** via *Security Credentials → Assign MFA device* in the IAM console.

> 💡 **Exam Tip:** Always enable MFA on the root user and privileged IAM users.

---

## Access Keys, CLI, and SDK

AWS can be managed in multiple ways:

- **Management Console:** Web interface (login with username + password)
- **CLI (Command Line Interface):** Authenticate using Access Key / Secret Access Key.
- **SDKs:** Programmatic access in languages like Python (Boto3), Java, etc.

### CLI Configuration

1. Generate access keys:  
   IAM → Users → *username* → Security credentials → “Create access key”.
2. Configure the CLI:

   ```bash
   aws configure
   ```

   Then enter:
   - Access Key ID  
   - Secret Access Key  
   - Default region name (this can be derived from the management console)
   - Output format (e.g., json)

> 💡 **Tip:** Access keys should never be shared or **committed to code repositories**. Use **IAM Roles** or **AWS Vault** instead.

---

## IAM Roles

**Roles** provide *temporary* access to AWS resources for trusted entities.  
Instead of storing long-term credentials, a role is *assumed* by a service or user via the **Security Token Service (STS)**.

Example:

- An EC2 instance assumes a role that allows it to read from an S3 bucket.
- Lambda functions can assume a role to write logs to CloudWatch.

Advantages of IAM Roles:

- Temporary and automatically rotated credentials  
- Least-privilege enforcement  
- No need to hardcode secrets

> 💡 **Exam Tip:** Roles are used by:
>
> - AWS services (EC2, Lambda, etc.)
> - Cross-account access
> - Federated users (via SSO, Cognito, or external identity providers)

---

## IAM Security Tools

> 💡 **Exam-Relevant Overview**

While not a major topic, it helps to know the following:

- **IAM Credential Report:** Lists all users and their credential status (MFA enabled, keys age, etc.)
- **IAM Access Advisor:** Shows when services were last accessed by a user or role.
- **IAM Access Analyzer:** Helps identify overly permissive or cross-account access.

> 🧠 **Remember:** Use IAM security tools for auditing and compliance checks.

---

## Quick Review

| Concept         | Description                                 | Exam Hint                     |
|-----------------|---------------------------------------------|-------------------------------|
| Root Account    | Full control, use only for setup            | Enable MFA immediately        |
| User            | Identity with credentials                   | Belongs to one or more groups |
| Group           | Collection of users                         | Cannot contain other groups   |
| Role            | Temporary permissions for services or users | Uses STS                      |
| Policy          | JSON document defining permissions          | Deny > Allow                  |
| MFA             | Adds a second factor for security           | Strongly recommended          |
| CLI             | Programmatic access                         | Uses access keys              |
| Access Analyzer | Auditing tool                               | Detects cross-account access  |
