# Ecosystem fit and the contribution we want to make

Checked: 2026-10-25, America/Los_Angeles. Research and sharing preparation only; no outreach, endorsement or production integration.

## The proposal

Make scoped operational evidence portable enough for a shopper's agent to use, verify and explain. Let existing commerce protocols carry discovery and transactions; make this evidence optional, explicitly attributed, and independently consumable. Give merchants a way to demonstrate their service through comparable methods without purchasing a favorable verdict.

The consumer demonstration asks whether evidence changes a choice under a person's stated constraints. It can demonstrate deterministic behavior and uncertainty handling. Consumer preference, merchant sales benefit and real-world recommendation improvement require testing with actual participants.

## Where each audience fits

| Audience | Existing surface | Useful question for this project |
|---|---|---|
| Shopify / UCP builders | UCP agent tooling, Catalog and supported capability composition | Can an optional merchant-evidence reference help a consumer surface explain service tradeoffs while preserving catalog and checkout interoperability? |
| Google / UCP contributors | UCP schemas, capabilities, governance and consumer surfaces | Is the demonstrated vendor catalog-reference mechanism a useful experimental boundary, and which test vectors would make its scope clearer? |
| OpenAI / Stripe ACP contributors | ACP specifications and each deployed integration contract | Is there a supported independent evidence-reference/enrichment path? Which merchant-versus-product distinctions should consumers preserve? |
| Square / UCP Food TC and Square developers | UCP Food TC participation; Square commerce APIs, merchant-authorized access and MCP | Which authorized order/refund observations can support a properly defined claim, and which promise/delivery/history gaps need separate sources? |
| Personal Agent Protocol participants | Draft company discovery, user authorization and sessions across APIs, web and conversations | Could a company's authorized API expose optional aggregate evidence while discovery and access remain with the existing protocol? |

These are different roles. A company being a prospective integration audience does not establish that it maintains a protocol, adopted this project, or ingests its claims.

## Fresh official observations

[Shopify's June 17 Spring '26 developer announcement](https://www.shopify.com/news/spring-26-edition-dev) describes self-serve UCP access through agent-profile registration and MCP, and Catalog access through an API key without prior approval. This removes a generic partnership-approval assumption. It does not grant access to private operational data or authorize aggregate publication.

[Google's March 19 UCP update](https://blog.google/products-and-platforms/products/shopping/ucp-updates/) describes optional Cart, Catalog and Identity Linking capabilities, with Google-surface onboarding discussed separately. A supported protocol integration and distribution on a particular platform are separate questions.

[Square's MCP documentation](https://developer.squareup.com/docs/mcp) describes OAuth-scoped API access, remote production resources, local sandbox testing, client allowlisting and a local read-only setting. This establishes an integration surface, not OCP adoption or automatic UCP support. No connection is made in this reference.

The [official UCP announcements](https://ucp.dev/documentation/announcements/#july-16-2026-food-technical-council-food-tc-formed) confirm that Block (Square), DoorDash, Google, Toast and Uber Eats formed the Food Technical Council on July 16. Square is therefore an existing UCP ecosystem participant. This does not establish deployment of our evidence format, and shipped grocery cohorts cannot silently become restaurant or local-delivery comparisons.

The [Square fulfillment guide](https://developer.squareup.com/docs/orders-api/fulfillments) places delivery details behind restricted access and distinguishes fulfillment state from delivery observations. The [delivery-details object](https://developer.squareup.com/reference/square/objects/OrderFulfillmentDeliveryDetails) describes separate completion and delivery timestamps. A source field alone does not independently authenticate the physical event or preserve the original promise.

The [Square PaymentRefund reference](https://developer.squareup.com/reference/square/objects/PaymentRefund?redirect_hash=navsection-oauth), observed at API version `2026-09-16`, distinguishes current refund status, creation time and last update. Last update is not a guaranteed settlement-transition timestamp. An exact settled-refund window needs adequate event evidence or an explicitly different metric; missing evidence stays unknown.

For current upstream versions, immutable commits, unresolved proposals and schema constraints, see [ADR 0001](ADRs/0001-upstream-alignment.md). Company announcements provide product direction; released normative schemas and actual service contracts govern implementation.

## New adjacent work: Personal Agent Protocol and W3C/GS1

[Sierra's October 6 announcement](https://sierra.ai/blog/introducing-personal-agent-protocol) names Meta and Sierra as developers of Personal Agent Protocol, with partners including Shopify, Stripe and Walmart. That is a separate discovery/authorization effort, not evidence that these companies adopted OCP.

The [live official specification](https://personalagentprotocol.org/docs/0.3/spec) identifies draft **0.3**. Its [changelog](https://personalagentprotocol.org/docs/changelog) calls 0.3 **in progress** and documents breaking changes. Direct Markdown retrieval on October 25 redirected to `/docs/0.3/spec.md`; SHA256 was `749f9f2b68ddfa509d8d19955de7856e653c72480c42d1d0b496f88836e465bd`. Treat this as working draft material, not a stable release.

The [canonical public repository](https://github.com/personal-agent-protocol/personal-agent-protocol), linked from the official site, was observed at `39b35bdf240fc07f157d6ca4e29b5a41d4b36b5d`, dated October 19. No GitHub tags or releases were returned. Its `content/versions/versions.json` listed 0.2 and frozen 0.1, so the public HEAD snapshot must not be represented as the source of the live 0.3 draft. Recheck both sources before implementing an integration. This reference implements no Poppy discovery, authorization, session or conversation endpoints.

The [W3C/GS1 workshop agenda](https://www.w3.org/2026/ecommerce-agents/agenda.html) includes merchant perspectives, product identity, data authority, delegation and trust discussions. These are workshop presentations and position statements, not adopted W3C standards. They reinforce useful questions for our proposal: who is authorized to make a claim, what exact subject it covers, and whether a consumer can interpret it safely. Merchant operational claims remain separate from product-version identity and physical quality.

## What makes a useful contribution

Give another developer an example they can run, a small contract they can inspect, and a precise question they can answer. Show both an unsupported client retaining base behavior and an opted-in client reading the extra evidence. Include adversarial examples and unresolved trust/source-authenticity limitations.

Keep the initial ask narrow: feedback on the demonstrated integration boundary and evidence semantics. An unsolicited replacement protocol, a broad partnership request, or a claim that platforms should change their rankings would be harder to evaluate.

Use UCP's existing contribution and namespace guidance for UCP work and ACP's separate governance for ACP work. Square's official developer forum/partner routes are a data-integration discussion path. No actual post, request, registration or message is authorized by this document.

## Merchant value hypothesis

A merchant with useful service evidence can explain why it fits a buyer's priorities, even if it is not the cheapest or most heavily promoted option. The reference should show that situation alongside a price-first shopper legitimately choosing another merchant. Merchant participation cannot buy preferential placement.

Participation should make the publication scope understandable: exact method, cohort, coverage, source limitations, conflicts and withdrawal status. The preview must expose unfavorable and unknown results together. It must keep consumer/order records out of the public contract and distinguish API access from publication consent.

No conversion, revenue or distribution lift is established yet. Those are pilot outcomes to measure, not benefits to advertise as proven.

## Sharing package

Prepare a concise walkthrough, runnable repository/archive, consumer and merchant screenshots, compatibility example, evidence methods, threat model, contribution draft and transparent gap report. Repository publication under Apache-2.0 was authorized on October 26, 2026; the license and notices are included. Hosted deployment and named outreach remain separate decisions.
