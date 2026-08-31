# Domain Examples

The core methodology (34 handles, four protocols) is domain-agnostic — nothing here is required reading. This folder holds companion docs that show the methodology applied to a specific platform: what each handle actually checks, and what its findings look like, in that domain's own terms.

## Current

- **[salesforce/](salesforce/)** — Apex, OmniStudio, Financial Services Cloud. [salesforce-handles.md](salesforce/salesforce-handles.md) maps handles to platform-specific checks and finding shapes; [salesforce-triangle.md](salesforce/salesforce-triangle.md) adapts the Triangle Protocol's output skeleton to Salesforce artifacts.

## Adding a domain

`CONTRIBUTING.md` welcomes examples outside Salesforce/Azure — frontend frameworks, data pipelines, mobile, systems programming, DevOps/IaC. To add one:

1. Create `examples/<domain>/`.
2. At minimum, a `<domain>-handles.md` mapping a handful of high-value handles to what they check in that domain and what a finding looks like there — follow `salesforce-handles.md`'s shape (artifact → verbatim evidence → what's wrong → why it matters).
3. Optionally, a `<domain>-triangle.md` if the domain has a natural TQ/TC/CQ output skeleton worth documenting (see `salesforce-triangle.md`).
4. Link the new files from this README, and from `README.md`'s reference table and any protocol doc they extend (see how `triangle-protocol.md` links Salesforce as a "domain-specific companion").
