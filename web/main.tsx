import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Button, Chip, Modal, Spinner} from '@heroui/react';
import './style.css';

type Metric = {id:string;status:string;value:number|null;numerator:number|null;denominator:number|null;coverage_fraction:number|null;reason:string;followup_days:number;lower_bound:number|null;upper_bound:number|null};
type Statement = {statement_id:string;metric:Metric;period:{start:string;end:string};observed_at:string;expires_at:string;methodology_url:string;refund_policy:{id:string};[key:string]:unknown};
type Evidence = {statement:Statement;verification:{signature_valid:boolean;current:boolean;calculation_reproduced:boolean;source_truth:string};envelope:unknown};
type Merchant = {subject:string;name:string;evidence:Evidence[]};
type Bundle = {merchants:Merchant[];demo_clock:string};
type Decision = {choice:string|null;state:string;reason:string;limitations:string;assessments:{subject:string;price:number;eligible:boolean;reason:string;historical_on_time:number|null}[]};
type Scenario = {preference:{label:string;max_price:number;min_historical_on_time:number|null};decision:Decision;without_evidence:Decision};
const labels:Record<string,string> = {fulfilled_on_time_rate:'Delivered on time and in full',order_complete_rate:'Complete at recorded fulfillment',order_refund_incidence:'Orders with settled refunds'};
const metricIds = Object.keys(labels);
function App(){
  const [bundle,setBundle]=useState<Bundle|null>(null), [scenarios,setScenarios]=useState<Record<string,Scenario>|null>(null);
  const [failure,setFailure]=useState(false),[selection,setSelection]=useState('delivery'),[withEvidence,setWithEvidence]=useState(true);
  const [detail,setDetail]=useState<{title:string;body:unknown}|null>(null);
  async function load(){setFailure(false);setBundle(null);try{const [a,b]=await Promise.all([fetch('/v0/demo'),fetch('/v0/scenarios')]);if(!a.ok||!b.ok)throw Error();setBundle(await a.json());setScenarios(await b.json());}catch{setFailure(true)}}
  useEffect(()=>{void load()},[]);
  const name=(id:string|null)=>bundle?.merchants.find(x=>x.subject===id)?.name ?? 'Insufficient evidence';
  const scenario=scenarios?.[selection];
  const decision=withEvidence?scenario?.decision:scenario?.without_evidence;
  const selectedEvidence=detail&&typeof detail.body==='object'&&detail.body&&'statement' in detail.body?detail.body as Evidence:null;
  return <main>
    <div className="notice"><strong>Synthetic demonstration · experimental 0.2.0</strong><br/>Fictional merchants and outcomes. No real merchant data, independent audit or standards endorsement.<br/>Demo clock: {bundle?.demo_clock??'loading…'} · explicitly simulated</div>
    <header><div><h1>Open Commerce Performance</h1><p className="subtle">Choose with operational evidence, your budget and your priorities.</p></div><a className="button button--secondary" href="/v0/.well-known/ocp">Agent-readable JSON</a></header>
    {failure?<div role="alert"><h2>Evidence could not be loaded</h2><p>No decision has been calculated from this failed read.</p><Button onPress={()=>void load()}>Retry</Button></div>:!bundle||!scenarios?<div role="status"><Spinner/> Loading synthetic evidence…</div>:<>
      <section aria-labelledby="shopper"><h2 id="shopper">Your shopping priorities</h2><p>Same fictional grocery box, in stock at each merchant. Landed prices are fixed across both evidence modes.</p>
      <div className="methods" role="group" aria-label="Shopping scenario">{Object.entries(scenarios).map(([id,s])=><Button key={id} variant={selection===id?'primary':'secondary'} aria-pressed={selection===id} onPress={()=>setSelection(id)}>{s.preference.label}</Button>)}</div>
      <div className="methods" role="group" aria-label="Evidence mode"><Button variant={withEvidence?'primary':'secondary'} aria-pressed={withEvidence} onPress={()=>setWithEvidence(true)}>With operational evidence</Button><Button variant={!withEvidence?'primary':'secondary'} aria-pressed={!withEvidence} onPress={()=>setWithEvidence(false)}>Without operational evidence</Button></div>
      <div className="decision" aria-live="polite"><div><span className="subtle">{decision?.choice?'Policy demonstration selects':'Policy demonstration abstains'}</span><h2>{name(decision?.choice??null)}</h2><p>{decision?.reason}</p></div><Chip size="sm" variant="soft">{decision?.state.replaceAll('_',' ')}</Chip></div>
      <div className="assessment-list">{decision?.assessments.map(a=><div className="proof-row" key={a.subject}><strong>{name(a.subject)} · ${a.price}</strong><span className="subtle">{a.reason}</span></div>)}</div>
      <p className="details">Delivery preference: historical cohort on-time/in-full rate ≥85%. This describes past synthetic records and does not promise your delivery. Missing evidence is never poor performance. Refund incidence does not determine this choice.</p></section>
      <section aria-labelledby="comparison"><h2 id="comparison" className="section-heading">Inspect the evidence</h2><p className="subtle">Purchase cohort: April 1–June 30, 2026 · observed October 25 · US, shipped, standard service.</p>
      {!bundle.merchants.some(m=>m.evidence.length)?<div role="status">No current published statements. Expired or withdrawn evidence cannot support a decision.</div>:<div className="table-scroll" role="region" aria-label="Merchant evidence comparison" tabIndex={0}><table><thead><tr><th scope="col">Operational measure</th>{bundle.merchants.map(m=><th scope="col" key={m.subject}>{m.name}<div className="details">Fictional · no universal score</div></th>)}</tr></thead><tbody>
      {metricIds.map(id=><tr key={id}><th scope="row">{labels[id]}<div className="details">{id==='order_refund_incidence'?'60-day follow-up. A refund is not a product defect.':id==='order_complete_rate'?'Recorded fulfillment, not doorstep delivery.':'Original checkout promise + separate synthetic delivery source.'}</div><Button size="sm" variant="tertiary" onPress={async()=>{const r=await fetch(`/v0/methods/${id}/0.2.0`);setDetail({title:labels[id],body:r.ok?await r.json():{error:'Method could not be loaded'}})}}>Method</Button></th>{bundle.merchants.map(merchant=>{const evidence=merchant.evidence.find(e=>e.statement.metric.id===id);const m=evidence?.statement.metric;return <td key={merchant.subject}>{!m?<span>No current evidence</span>:<><div className="number">{m.value===null?'Unknown':`${(m.value*100).toFixed(1)}%`}</div><div className="details">{m.value===null?m.status.replaceAll('_',' '):`${m.numerator} / ${m.denominator} orders`}<br/>{m.coverage_fraction===null?'Coverage unavailable':`${(m.coverage_fraction*100).toFixed(0)}% signal coverage`}<br/>Synthetic source</div><Button size="sm" variant="tertiary" onPress={()=>setDetail({title:`${merchant.name} · ${labels[id]}`,body:evidence})}>Inspect statement</Button></>}</td>})}</tr>)}</tbody></table></div>}
      </section>
      <section aria-labelledby="proof"><h2 id="proof">What has been checked</h2>{bundle.merchants.map(m=>{const v=m.evidence[0]?.verification;return <div className="proof-row" key={m.subject}><strong>{m.name}</strong><Chip size="sm" variant="soft">{v?.signature_valid?'Signed bytes valid':'No current proof'}</Chip><span>{v?.calculation_reproduced?'Recomputed by this local publisher':'Calculation unavailable'}</span><span className="subtle">Source truth: not established</span></div>})}<p>Signature validity, reproducible arithmetic and source truth are separate. These keys are ephemeral local fixtures. Evidence expires after seven days; status and consent are rechecked on every read.</p>
      <div className="methods"><a className="button button--secondary" href="/v0/schema/0.2.0">Experimental schema</a><a className="button button--secondary" href="/v0/scenarios">Decision trace JSON</a></div></section>
    </>}
    {detail&&<Modal.Backdrop isOpen onOpenChange={open=>!open&&setDetail(null)}><Modal.Container><Modal.Dialog><Modal.CloseTrigger/><Modal.Header><Modal.Heading>{detail.title}</Modal.Heading></Modal.Header><Modal.Body><p className="modal-copy">Fictional evidence only. Signed origin does not establish independent truth.</p>{selectedEvidence?<><dl className="evidence-summary">
<dt>Claim</dt><dd>{selectedEvidence.statement.metric.value===null?selectedEvidence.statement.metric.status.replaceAll('_',' '):`${selectedEvidence.statement.metric.numerator} / ${selectedEvidence.statement.metric.denominator} orders (${(selectedEvidence.statement.metric.value*100).toFixed(1)}%)`}</dd>
<dt>Purchase cohort</dt><dd>{selectedEvidence.statement.period.start} through {selectedEvidence.statement.period.end} (end exclusive)</dd>
<dt>Last observed / expires</dt><dd>{selectedEvidence.statement.observed_at} / {selectedEvidence.statement.expires_at}</dd>
<dt>Scope</dt><dd>Merchant operations · US · shipped · standard service · general commerce</dd>
<dt>Source</dt><dd>Synthetic fixture with separate promise/delivery inputs. No real carrier data.</dd>
<dt>Signed origin / current status</dt><dd>{selectedEvidence.verification.signature_valid?'Valid JWS signed bytes':'Invalid signed bytes'} · {selectedEvidence.verification.current?'current in the demo clock':'not current'}</dd>
<dt>Calculation</dt><dd>{selectedEvidence.verification.calculation_reproduced?'Recomputed from the fixture by this local publisher. This is not an independent third-party audit.':'Not recomputed.'}</dd>
<dt>Source truth / audit</dt><dd>Not established / not independently audited. Cryptography does not prove the input records true.</dd>
<dt>Refund policy</dt><dd>{selectedEvidence.statement.refund_policy.id.replaceAll('-',' ')}. Refund incidence is not product quality.</dd>
<dt>Issuer and conflict</dt><dd>Black 4 fixture issuer · Black 4 local research · no placement or affiliate payments.</dd>
</dl><details><summary>Developer JSON and JWS envelope</summary><pre>{JSON.stringify(detail.body,null,2)}</pre></details></>:<pre>{JSON.stringify(detail.body,null,2)}</pre>}</Modal.Body><Modal.Footer><Button onPress={()=>setDetail(null)}>Close</Button></Modal.Footer></Modal.Dialog></Modal.Container></Modal.Backdrop>}
    <footer className="details">Local policy simulation, not model or consumer validation. No paid placement, product reliability claim, checkout or purchasing.</footer>
  </main>
}
createRoot(document.getElementById('root')!).render(<App/>);
