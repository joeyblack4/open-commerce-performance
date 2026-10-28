# Portable business evidence for AI recommendations

Consumers deserve recommendations grounded in what a business can actually deliver. Businesses deserve a way to earn consideration through the service they provide. Today's discovery incentives can work against both.

Open Commerce Performance proposes **portable evidence about a business that an agent can consult during discovery and selection**. Businesses choose what to publish. A system of record or an identified calculation service attests to a defined result. Participating AI platforms use relevant evidence to assess a business against the buyer's needs, explain their reasoning and disclose commercial interests.

The goal is to make service a stronger basis for competition and give consumers better grounds for a decision. These are outcomes to test, not results established by the prototype.

## The problem with today's discovery

A consumer asks where to eat, which brand to buy or which service company to trust. The answer can arrive through an ad auction, an affiliate comparison or a sponsored creator. Each has an economic incentive that can differ from the consumer's objective.

**Advertising buys access to attention.** A bid can help determine where an ad appears. It does not establish whether the business will meet this buyer's delivery deadline, service expectation or budget. Google's own [Ad Rank explanation](https://support.google.com/google-ads/answer/1722122?hl=en) includes bids alongside relevance, quality and other auction factors. Spending matters; it is not the only factor and it does not buy every organic result.

**Affiliate recommendations can pay when the consumer buys.** A higher commission or a commercial agreement can conflict with recommending the best fit. That conflict has produced real enforcement cases: in its [2020 LendEDU settlement announcement](https://www.ftc.gov/news-events/news/press-releases/2020/05/ftc-finalizes-settlement-lendedu-case-related-deceptive-rankings-fake-reviews), the FTC described allegations that companies obtained higher rankings and ratings by paying for placement while the site presented its information as objective. This is a documented case, not a claim about every affiliate publisher or the company's current practices.

**Influence can substitute for a service record.** An endorsement may reflect a paid relationship, a gifted experience or one person's visit. A convincing post cannot by itself establish what ordinary customers generally receive. The FTC's [endorsement guidance](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) explains why material relationships affect how people evaluate recommendations. A [2018 study by Mathur, Narayanan and Chetty](https://arxiv.org/abs/1809.00620) found disclosure in only about 10% of the affiliate content it identified on YouTube and Pinterest; a 1,791-person user study found that short, unexplained disclosure wording was poorly understood. Those findings describe that historical sample, not today's prevalence across the internet.

Fake reviews and suppressed criticism can further distort the picture. The FTC's [2024 announcement on fake reviews and testimonials](https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials) describes these practices and their effect on consumers and honest competitors. It does not establish that every review, influencer or recommendation is unreliable.

The consumer bears the consequences: an order that misses the occasion, a lunch break spent waiting, an unexpected invoice or hours trying to reach support. A business that delivers dependable service can still struggle to make that performance visible. The commercial reward can go to whoever earns the click or sale before the quality of the experience becomes apparent.

Disclosing an incentive helps a consumer interpret a recommendation. It still does not answer whether a business performs well on the thing that matters to them. That is the information this proposal aims to make available.

## AI makes this choice consequential

An agent can turn a confusing search into one confident answer. If it relies on promotional material or quietly favors commission-paying partners, it can reproduce the same incentive problem while giving the consumer fewer visible alternatives. That is a design risk, not a claim that every AI platform currently behaves this way.

The opportunity is to give agents a different input: relevant operational evidence with a named source, a defined calculation and visible limits. For a buyer who needs reliable delivery, the agent could examine delivery against original promises. For a short lunch break, it could examine pickup preparation history. A restaurant's popularity or a brand's marketing budget does not answer either question.

The consumer should be able to see why the evidence mattered, what the agent still does not know and whether anyone is being paid in connection with the recommendation. Making checkout easier is useful. Helping people choose the right business must be part of the commerce stack too.

## The proposal

Agree on a common format for publishing business evidence. Leave the choice of metrics open.

A restaurant might publish its average net check or recorded pickup preparation time. An ecommerce brand might publish delivery outcomes when it has the original promise and carrier observations. A B2B service company might publish response time from its support system. Each claim has its own definition, population and limitations. None becomes a universal rating of the business.

A business should be able to authorize publication inside a system it already uses, or through an authorized service using that system. It should not need to operate signing infrastructure or move its records into a new central database. Evidence should be portable across discovery providers and AI platforms.

## How it works

1. **Choose evidence.** The business selects a supported metric and sees its definition, scope and exact publication preview. Reading private records and publishing aggregates are separate permissions.
2. **Calculate and attest.** The source provider or a named service computes the result over the declared eligible population. It discloses missing data and what it actually checked, then signs the claim.
3. **Publish with permission.** The business authorizes the aggregate with its method, source coverage, issuer, measurement period and current status. Private transaction and customer records stay behind the source boundary.
4. **Retrieve and assess.** An agent checks identity, signature, status, method, freshness and relevance. It cites claims that influenced its explanation and identifies unanswered questions.
5. **Refresh and correct.** Later observations produce new versions. Expiry, correction, dispute and withdrawal remain visible; a cached signature cannot restore a withdrawn feed's current status.

The reference is a synthetic demonstration with a public static replay and a local runtime. It is not a global discovery implementation or a source-provider endorsement.

## What the standard defines

| Part | Required meaning |
| --- | --- |
| Business | Responsible entity or location and its identity binding. A branch's record does not automatically describe a brand. |
| Metric | Public, versioned definition, unit, calculation and intended interpretation. |
| Population | Period, service or channel, eligibility, exclusions, sample size and missing-data coverage. |
| Result | Value and supporting aggregate counts, or an explicit unknown or suppressed state. |
| Attestation | Source systems, named issuer, scope of checking, funding relationship and cryptographic protection. |
| Lifecycle | Observation and issue times, expiry, current status and correction or withdrawal references. |

New metric definitions should not require a core protocol release. Providers, businesses and industry groups can define methods. Shared methods enable comparisons; unfamiliar methods need review. Matching names are insufficient: comparison requires compatible definitions, populations, units and windows. An AI must not silently equate different meanings of "on time."

The [claim schema](../spec/schemas/portable-claim.schema.json) and [protocol proposal](PORTABLE_EVIDENCE_PROTOCOL.md) make this concrete. They are a candidate profile, not a ratified standard. The existing 0.2 reference remains a narrower technical example.

## What verification means

**Provider-issued** means the source provider takes responsibility for the declared calculation and scope. **Service-calculated** means a named service takes responsibility for its extraction and calculation using source records. API access does not imply provider endorsement. **Business-asserted** identifies a claim without either source calculation assurance.

A signature authenticates the issuer and protects the signed bytes. It does not establish whether staff entered accurate data or every transaction reached the source. Reproducible arithmetic, complete coverage, independent observation and independent audit are different assurances. The [W3C Verifiable Credentials trust model](https://www.w3.org/TR/vc-data-model-2.0/#trust-model) preserves a similar distinction. This reference uses JWS and does not claim VC conformance.

## Business choice and consumer protection

Businesses choose metrics; they cannot change a published method's meaning or quietly remove unfavorable eligible records. A limited channel or location can be a valid population when prominently disclosed. A verifier accounts for the population it can observe and identifies boundaries it cannot establish.

Voluntary publication remains selective. An unpublished return rate is unknown, not zero. Five favorable measures do not establish superiority over a business publishing one. Shipping performance does not establish product quality; a low refund rate can reflect restrictive policies. New or unconnected businesses retain other routes to consideration.

Publication must minimize private data, suppress unsafe aggregates and consider repeated-release inference. Withdrawal ends current use under the publication contract; it cannot promise deletion of every prior copy. Retention and historical-status rules need agreement before a live pilot. No global customer identity or cross-business purchase tracking is required.

## Where it fits

**Candidate discovery → business identity → relevant evidence → a recommendation for this buyer → existing commerce transaction.**

Candidate discovery comes from search, maps, directories, marketplaces and agent indexes. Evidence helps assess discovered businesses. The agent owns the recommendation; UCP and other supported commerce interfaces carry subsequent catalog, checkout and order interactions. Payment authorization stays with its existing owners.

Evidence should be retrievable without requiring a purchase. UCP's [third-party extension model](https://ucp.dev/specification/overview/#third-party-extensions-comvendor-orgorg) offers an integration option to evaluate. The existing catalog fixture is an offline test against pinned released schemas. No live UCP discovery or platform ingestion is claimed.

Any capable agent could consume this format without an exclusive index or mandatory Black 4 service. Actual use requires AI-platform implementation and choices about trusted issuers. Publication alone cannot make every AI retrieve or trust it. Claim text is data, never executable instructions.

## Participation and competition

For a system of record, permissioned evidence publication could make its operational records more useful to customers outside its own interface. Providers preserve their definitions and source boundaries. Businesses gain portable evidence of improvements in service. AI platforms gain structured support for accountable recommendation explanations.

An open standard needs multiple issuers, affordable participation, transparent methods, public change review and a way to challenge errors. Calculation or hosting fees must not purchase a favorable verdict or undisclosed ranking advantage. Governance should include small businesses and consumers alongside source providers and AI companies. Black 4 is proposing a reference and convening discussion; no consortium or partnership exists.

The economic bet is that a business can make a service improvement, publish evidence of it and become more relevant to buyers who care about that service. Better dispatch, clearer billing or faster support would then have a route into discovery. Advertising can still introduce a business; evidence gives the consumer and agent another basis for assessing it. We need to test whether that changes exposure and realized outcomes rather than assuming that an open format makes markets fair.

## A responsibility for recommendation platforms

An evidence protocol cannot make a platform act in the buyer's interest. Systems of record can attest to calculations; AI platforms control candidate selection, commercial arrangements and recommendations. A live pilot needs explicit commitments from both.

1. **Assess fit against the buyer's request.** Advertising spend, affiliate commission and payment for verification must not improve the assessment of the same evidence. Sponsored placement must be identified separately from the assessment.
2. **Show the commercial relationship.** Disclose sponsorship, affiliate compensation and ownership interests affecting a recommendation. A source issuer's relationship to the business and a recommender's incentive are separate facts.
3. **Keep consideration open.** An agent must not silently exclude a business solely because it offers no commission, uses a different source provider or has not purchased a badge. Limited or missing history stays unknown; useful alternatives and other evidence remain eligible.
4. **Explain the decision.** Cite the claims that mattered, describe their scope and limits, and distinguish observed history from a promise about the next purchase. Allow errors to be challenged and corrected.

These are proposed participation commitments, not properties a signature enforces or a certification the current reference awards. The candidate claim schema describes business evidence. Commercial interests and sponsored placement belong in a separate recommendation disclosure; that exchange and enforcement remain to be designed with agent platforms.

Voluntary disclosure can favor businesses with favorable metrics. Open publication also cannot rescue a business that an agent never considers. Auditing omissions, participation costs and platform incentives is essential. Without that work, this could become another paid badge layered onto the same discovery system.

## The first alignment request

Ask a small founding group of systems of record and AI platforms to:

1. Nominate a product and technical owner to review the format and publication lifecycle.
2. Identify one native metric each source provider could responsibly issue today, including its limitations.
3. Run a consented pilot exchanging claims from two source systems through two independent agent implementations.

First establish that independent consumers interpret portable claims consistently. Then compare the same candidate set with and without evidence. Keep the claims and buyer request fixed while varying commission offers or advertising spend: those changes must not improve the evidence-based assessment, and sponsored placement must remain visibly separate. This is a proposed pilot test; the current reference has no advertising or commission inputs.

Measure comprehension, realized cost, missed commitments, time spent resolving problems and regret. Separately assess smaller-business exposure, participation cost, businesses omitted before assessment and treatment of limited history. Conversion or a changed recommendation alone is insufficient. The question is whether people make choices that work out better for them, and whether businesses can win those choices by improving service.

The [CEO brief](CEO_BRIEF.md) carries the request. The [walkthrough](SHARE_PACKAGE.md) distinguishes implemented synthetic behavior from the live integrations and adoption still required.
