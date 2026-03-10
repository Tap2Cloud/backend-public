# Tap2Cloud (t2c)

![Open Source](https://img.shields.io/badge/Open%20Source-Open%20Core-green)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange)
![EU DPP](https://img.shields.io/badge/Digital%20Product%20Passport-Compatible-blue)

**Tap2Cloud (t2c)** is an **open-core platform** for managing **Digital Product Passports (DPP)** and **asset lifecycle data**.

The platform provides infrastructure for organizations to create, manage, and exchange structured product data required for **sustainability reporting, regulatory compliance, and circular economy initiatives**.

Tap2Cloud supports emerging **Digital Product Passport ecosystems**, including the **EU Battery Passport**, which will become mandatory for certain batteries from **February 2027** under the EU Battery Regulation.

> **Important:** This repository contains the **open-source core** of Tap2Cloud.  
> **Not all Tap2Cloud components are open source.** Some capabilities are only partially available here, and some features of the full Tap2Cloud platform are provided through **separate proprietary modules or services**.  
> This applies in particular to parts of **organizational management**, such as **advanced access control, enterprise identity management, and extended governance tooling**.

---

# Vision

Tap2Cloud aims to provide a **modular infrastructure layer for product lifecycle transparency**, enabling companies to manage complex product data across supply chains and regulatory frameworks.

The platform focuses on:

- product lifecycle data management
- regulatory compliance support
- supply chain transparency
- interoperability with digital product passport ecosystems
- circular economy enablement

---

# Digital Product Passport Context

The European Union is introducing **Digital Product Passports (DPP)** to improve transparency across product lifecycles and support sustainable product design.

The **EU Battery Regulation (2023/1542)** introduces the first mandatory passport system for batteries, requiring lifecycle data about materials, carbon footprint, supply chain due diligence, circularity, and performance.

The battery passport is considered the **first sector-specific implementation of the broader Digital Product Passport framework**, which will later extend to other industries.

Tap2Cloud is designed to support these evolving regulatory ecosystems.

---

# Open Core Model

Tap2Cloud follows an **Open Core model**.

This means:

- a **core platform** is released as open source in this repository
- some **advanced capabilities, integrations, and enterprise features** are maintained separately
- the open-source repository provides the **foundation** for Digital Product Passport data management
- the complete Tap2Cloud platform includes additional capabilities that are **not part of this repository**

The goal is to:

- enable an open ecosystem around Digital Product Passports
- allow developers and organizations to build on top of the core platform
- support enterprise deployments with additional capabilities

---

# Open Source Scope

This repository contains **core platform components**, including:

- asset categories
- asset type management
- asset lifecycle tracking
- asset pass management
- documentation modules
- service records
- audit records
- taxonomy management
- basic process modeling

These modules provide the **core data infrastructure for Digital Product Passport systems**.

---

# Components with Limited Open Source Availability

Some parts of the Tap2Cloud platform are **partially implemented in this repository but depend on non-open-source components for full functionality**.

These limitations exist mainly in platform management and enterprise infrastructure areas.

## Organizational Management

The repository includes **basic structures related to organizational entities**, such as:

- Organizations
- Users

However, the full capabilities related to these entities may rely on **external services or proprietary modules**, including:

- advanced access control
- enterprise identity management
- extended governance and administration tools

As a result, **some management functionality available in the full Tap2Cloud platform is not fully accessible in this open-source repository**.

---

# Proprietary Platform Components

Certain components of the Tap2Cloud platform are **not open source and are maintained separately**.

Examples may include:

- enterprise deployment tooling
- advanced integrations
- compliance automation services
- hosted platform infrastructure
- specialized regulatory modules

This hybrid architecture allows the open ecosystem to evolve while supporting enterprise-scale deployments.

---

# Key Platform Features

## Asset & Product Management

- Asset categories
- Asset type management
- Asset lifecycle tracking
- Asset pass management

## Documentation & Compliance

- Instruction manuals
- Typeplates
- Service records
- Audit records

## Process Modeling

Tap2Cloud supports **basic process orchestration**, allowing multiple asset types to be chained together to represent lifecycle relationships.

---

# Taxonomy Management

Tap2Cloud supports configurable **data taxonomies**.

Examples include:

- **Battery Passport taxonomy** (fully implemented)
- **Digital Product Passport (DPP)** taxonomy (in development)

Future industry taxonomies may include:

- textiles
- toys
- tyres
- electronics
- construction products

---

# Architecture Overview

Tap2Cloud follows a **modular and extensible architecture** designed for interoperability with emerging digital infrastructure.

Applications / User Interfaces  
│  
Platform Services (Asset Management, Passport Services, Compliance Modules)  
│  
Data & Taxonomy Layer (Product Data Models, Passport Schemas)  
│  
Integration Layer (APIs, External Systems, Data Spaces)

The architecture allows integration with:

- supply chain traceability systems
- sustainability reporting tools
- European data space infrastructures

---

# Example Digital Passport Structure

```json
{
  "passport_id": "BATTERY-001",
  "product": {
    "type": "EV Battery",
    "manufacturer": "Example Manufacturer",
    "model": "Model X"
  },
  "carbon_footprint": {
    "total_emissions": 75.2,
    "unit": "kg CO2e/kWh"
  },
  "materials": {
    "lithium": "5.4%",
    "nickel": "12.8%"
  },
  "circularity": {
    "recycled_content": "18%",
    "recyclability": "92%"
  }
}
```

---

# Ecosystem Alignment

Tap2Cloud considers major regulatory and industry initiatives including:

- EU Battery Regulation (2023/1542)
- Ecodesign for Sustainable Products Regulation (ESPR)
- Digital Product Passport (DPP)
- Global Battery Alliance (GBA)
- CIRPASS
- Catena-X
- Corporate Sustainability Reporting Directive (CSRD)
- Extended Producer Responsibility (EPR)

These frameworks define many of the **data attributes, traceability requirements, and interoperability standards** for product passports.

---

# Development Status

Tap2Cloud is currently under **active development**.

Implemented components include:

- asset categories
- asset type management
- asset lifecycle management
- asset pass management
- documentation modules
- audit and service tracking
- organization management structures
- user management structures
- basic process orchestration

Additional modules and interfaces are being published progressively.

---

# Roadmap

Planned development areas include:

## Platform Capabilities

- advanced Digital Product Passport templates
- compliance automation
- versioning and data lineage
- lifecycle analytics

## Interoperability

- standardized DPP APIs
- integration with data space infrastructures
- traceability systems

## Industry Data Models

Expansion of taxonomies for multiple industries.

---

# Contributing

Contributions are welcome.

Areas where help is appreciated:

- data model design
- taxonomy development
- regulatory mappings
- feature development
- integrations
- documentation

Contribution guidelines will be added soon.
