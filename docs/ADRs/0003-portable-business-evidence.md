# ADR 0003 Portable business evidence

Accepted for experimental local implementation October 27 2026, following the owner's instruction to rewrite and simplify around portable evidence for business discovery and selection. This supersedes mandatory KPI and whole-bundle publication as product direction. It does not change the historical 0.2 contract in place.

Businesses choose supported metrics. Every claim retains a public versioned method, subject, issuer, population, coverage, result and lifecycle. A generic 0.3 candidate envelope supports separately defined methods. Providers and industries can introduce definitions; consuming agents must understand methods before interpretation.

The runtime uses a new bounded fictional preview and the existing JWS and signed-status primitives. No new service, credential store, identity authority or customer data pipeline is introduced. Unknown publication never becomes failure; an unchanged signature cannot bypass withdrawn or disputed status. Provider issuance, service calculation and business assertion remain distinct.

The existing 0.2 calculator, private-source tests, independent CLI and offline UCP fixture remain technical references. Their narrow accepted identities and metrics are not silently widened. The 0.3 local interpreter checks origin and status against explicitly supplied fixture trust and reports source truth separately. It is not a second live AI integration.

The open proposal, CEO brief and prepared email seek provider and AI-platform alignment on the format and a small interoperability pilot. No endorsement, consortium, outreach or deployment follows from this local change.
