# LOCAL DRAFT — ACP enrichment question

ACP and OpenAI's deployed feed contract differ from UCP. Checked source `7fdd78df677a94dce04c770644b0fbbb1401272b` has dated stable snapshot `2026-04-17`, no GitHub tags/releases and separate unreleased work. ACP extension negotiation does not authorize arbitrary feed fields.

[ACP #221](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/issues/221) and its follow-up ask about removed performance fields and documentation differences. The current [OpenAI feed spec](https://developers.openai.com/commerce/specs/feed) distinguishes product reviews, optional store-review setup, returns acceptance and policy. Merchant operational aggregates are none of these fields.

Our local OCP example supplies scoped populations, JWS origin, current signed status, coverage and source-truth limits. Would agents benefit from an optional independent evidence reference, and through what supported enrichment contract? We do not reintroduce `return_rate`, `popularity_score`, undocumented columns, or translate refunds into star ratings/product quality. A substantial change follows ACP's SEP/maintainer/CLA process. Nothing here authorizes submission or claims ChatGPT ingests OCP.
