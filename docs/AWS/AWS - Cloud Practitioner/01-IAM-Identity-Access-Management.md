---
title: "01 Iam Identity Access Management"
nav_exclude: true
---

# Introduction

*Identity Access Management* in AWS is composed of three major components,each of which is explained in more detail in subsequent sections, **Users**, **Groups**, **Policies**, **Roles**.

**Important:** *IAM* in AWS is a **Global** service meaning it is not bound to a single region.

## Users and Groups

A formal definition of user is not really required, suffice to say it represents an identity used to log-in to AWS services. **Groups** are used to organize users in groups so that *policies* can be applied to them.

Something worth mentioning is that there are two type of users, the ones to whcih *Console Access* is granted and those which are used programtically for example by a script. Main difference is the first logs in via username and password the latter uses **access keys**.

**Note:** In AWS groups can contain only users not other groups. Of course a user can be made part of multiple groups.
