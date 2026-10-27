# Portable business evidence for AI recommendations

Joey · Black 4 · October 27 2026

We are proposing an open standard for **portable evidence about a business that an agent can consult during discovery and selection**. We are asking systems of record and AI platforms to help define and test it together.

The objective is straightforward: help consumers choose businesses using relevant operational facts, and help businesses earn recommendations through performance they can substantiate.

## Give businesses a way to publish what they can prove

Systems of record hold information that could help buyers understand how a business operates. A restaurant's recorded pickup preparation time, a retailer's observed delivery performance or a service company's response history can answer questions that matter in a purchase decision. A business needs a practical way to make that evidence available across AI discovery surfaces with clear meaning and accountable provenance.

Our proposal lets **the business choose what to publish**, while its source provider or an identified calculation service attests to a specific result. A common format tells an agent what was measured, over which population and period, according to whom, with what coverage and current status. Private customer and transaction records stay behind the source boundary.

We do not need every industry to adopt the same KPIs. Providers and industry groups can supply versioned definitions suited to their records. Shared definitions enable comparisons; the common format lets many useful measures travel.

## Keep the responsibilities clear

The business authorizes publication. The issuer takes responsibility for the declared calculation and scope. The AI platform checks the claim and decides whether it is relevant to the consumer's needs. Existing commerce protocols support the resulting transaction.

A provider-issued claim must be distinguishable from a third party's calculation using provider data. A signature establishes origin and integrity; source accuracy, completeness and independent audit require additional evidence. A missing metric remains unknown. Choosing a metric must not permit quietly excluding unfavorable eligible records.

An agent could use a restaurant's pickup record to assess a short lunch break while recognizing that the same record says little about an anniversary dinner. It should explain the evidence that influenced its recommendation and the questions that remain. There is no universal business score.

## Make service improvements easier to discover

For source providers, this could make operational data more valuable to customers through permissioned publication. Providers retain their definitions and source boundaries. Businesses gain evidence they can reuse across discovery platforms. AI platforms gain structured support for more accountable recommendations.

The opportunity is to make demonstrable service a stronger basis for competition. Participation should be affordable and portable, with multiple issuers and no exclusive discovery gatekeeper. Publication or verification fees must not purchase a favorable verdict. Smaller and newer businesses must remain eligible for consideration when their history is limited.

## Start with a concrete interoperability test

We are seeking a small founding group of source providers and AI platforms to review a common claim format, select a few useful native measures and test their exchange. Each participant would nominate a product and technical owner. The first pilot would publish consented claims from two source systems and have two independent agent implementations retrieve, check and explain them consistently.

Success would first mean interoperable claims, meaningful permission and correction, and clear consumer explanations. We would then measure decision quality, realized service outcomes, participation costs and exposure for smaller businesses. Better consumer outcomes must be demonstrated.

Black 4 has an open-source experimental reference with a fictional demonstration. Real source-provider issuance, live integrations and AI-platform adoption are the work we want to align on. The standard should remain openly usable across providers and agents, with shared governance that includes businesses and consumers.

**Would you nominate a product and technical owner to help test a shared format for portable business evidence?**

Reference and proposal: https://github.com/joeyblack4/open-commerce-performance/blob/main/docs/BUSINESS_DISCOVERY_CONCEPT.md
