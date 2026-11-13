---
theme: default
title: SpeedLimit
layout: default
class: bg-slate-900 text-white
colorSchema: light
aspectRatio: 16/9
drawings:
  persist: false
---

<div class="text-amber-300 uppercase tracking-widest text-sm font-bold">Software Engineering in AI · Management briefing</div>

<div class="grid grid-cols-[1fr_210px] items-center gap-10 mt-14">
  <div>
    <div class="text-7xl font-black tracking-tight">SpeedLimit</div>
    <div class="text-3xl leading-snug mt-6">When should a road operator lower an 80 km/h speed limit?</div>
    <div class="mt-10 text-xl text-slate-300">Mario Palagyi &amp; Jerome Puthuparampil</div>
  </div>
  <div class="text-center">
    <div style="display:grid;place-items:center;width:190px;height:190px;border:16px solid #dc2626;border-radius:50%;background:#fff;color:#101820;font:bold 90px/1 Arial">80</div>
    <div class="mt-4 text-sm uppercase tracking-widest text-slate-300">Starting limit · km/h</div>
  </div>
</div>

<div class="absolute bottom-12 left-14 right-14 border-t-4 border-dashed border-amber-300"></div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">01 / The working prototype</div>

# How the app chooses a limit

The operator enters light, road water and temperature. The app checks two things each time it updates.

<div class="grid grid-cols-2 gap-12 mt-8">
  <div class="border-t-4 border-teal-700 pt-4">
    <div class="text-2xl font-bold mb-3">Weather and light</div>
    <div class="text-xl leading-snug">Darkness, or a wet road below freezing, triggers the neural network. It tries 70, 60, 50 and 40 km/h, looking for the highest speed with at most one predicted near-accident per hour.</div>
  </div>
  <div class="border-t-4 border-teal-700 pt-4">
    <div class="text-2xl font-bold mb-3">Air quality</div>
    <div class="text-xl leading-snug">The app checks current pollution and the next three hourly forecasts. Python selects the rule for the highest reading. A local language model returns a reduction, which the app validates.</div>
  </div>
</div>

<div class="mt-7 text-xl font-bold text-teal-800">The lower valid limit wins. If either check fails, the screen shows “decision incomplete.”</div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">02 / Training data</div>

# Which hours could the model learn from?

<div class="grid grid-cols-[0.85fr_1.15fr] gap-12 mt-8">
  <div>
    <div class="text-7xl font-black text-teal-800">405</div>
    <div class="mt-2 text-2xl font-bold">of 744 hours qualified</div>
    <div class="mt-5 text-xl leading-snug">For each usable hour, the model linked the starting road conditions and speed limit to the number of near-accidents that followed.</div>
  </div>
  <div class="border-l-2 border-slate-300 pl-8">
    <div class="text-xl font-bold">The limit changed during 329 hours</div>
    <div class="mt-2 mb-6 text-lg">We excluded those hours because an incident could have occurred under either limit.</div>
    <div class="text-xl font-bold">An empty log needed an assumption</div>
    <div class="mt-2 mb-6 text-lg">We counted zero events only in hours we assumed had complete records.</div>
    <div class="text-xl font-bold">The test used later hours</div>
    <div class="mt-2 text-lg">Only earlier sensor readings could fill a gap. Future readings stayed out of the prediction.</div>
  </div>
</div>

---
layout: default
class: bg-slate-900 text-white
---

<div class="text-sm font-bold tracking-widest text-amber-300 uppercase">03 / Recorded demonstration</div>

# One road, four scenarios

<div class="grid grid-cols-4 gap-4 mt-7 text-center">
  <div v-for="item in [{label:'Clear road',speed:80},{label:'Dark road',speed:40},{label:'Poor air forecast',speed:50},{label:'Dark + poor air',speed:40}]" :key="item.label">
    <div class="text-lg font-bold mb-3">{{ item.label }}</div>
    <div style="display:grid;place-items:center;width:107px;height:107px;margin:auto;border:10px solid #dc2626;border-radius:50%;background:white;color:#101820;font:bold 50px/1 Arial">{{ item.speed }}</div>
    <div class="mt-2 text-sm text-slate-300">km/h</div>
  </div>
</div>

<div class="border-l-4 border-amber-300 pl-5 mt-8">
  <div class="text-2xl font-bold text-amber-300">Why did the dark road get 40?</div>
  <div class="mt-2 text-xl leading-snug">Every candidate missed the target. The app displayed its fallback of 40 km/h and flagged the estimate of <b>2.33 near-accidents per hour</b>. There were no usable training hours at that speed.</div>
</div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">04 / Evidence for management</div>

# How much confidence did the tests earn?

<div class="grid grid-cols-2 gap-12 mt-9">
  <div>
    <div class="text-5xl font-black text-teal-800">64 + 5</div>
    <div class="text-xl font-bold mt-3">Software and local-model checks</div>
    <div class="text-xl mt-4 leading-snug">64 automated tests passed. Five separate checks used the actual local language model, including a case where clean air now gave way to a poor forecast.</div>
  </div>
  <div>
    <div class="text-5xl font-black text-teal-800">0.86 vs 0.91</div>
    <div class="text-xl font-bold mt-3">Average error in incidents per hour</div>
    <div class="text-xl mt-4 leading-snug">On the held-out test, the neural network narrowly beat a simple prediction that always used the training average. The simple prediction did better the following year.</div>
  </div>
</div>

<div class="border-t-2 border-slate-300 pt-4 mt-9 text-lg">The following year repeated the same sensor readings with different incidents. We still need observations from different road conditions.</div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">05 / Lessons and oversight</div>

# Where does human judgment belong?

| Project finding | Management implication |
|---|---|
| The classroom policy assigns speed reductions to pollution levels. | A road authority would need to justify and approve those reductions. |
| Early language-model prompts produced wrong answers even for simple pollution bands. | Python now selects the applicable rule and checks the reply. An invalid answer leaves the decision incomplete. |
| Sensor identities and event-log coverage remain uncertain. | A data owner should confirm which sensors measured temperature and when an empty log means zero events. |

<div class="mt-6 text-lg text-teal-800"><b>Two uses of AI:</b> A coding assistant wrote the code and tests. The local language model runs inside the finished app.</div>

---
layout: default
class: bg-slate-900 text-white
---

<div class="text-sm font-bold tracking-widest text-amber-300 uppercase">06 / Recommendation</div>

<div class="mt-9 text-5xl font-black leading-tight">Keep SpeedLimit in<br>classroom validation.</div>

<div class="mt-6 max-w-3xl text-2xl leading-snug text-slate-200">Before considering a road trial, confirm the incident records and collect independent observations at lower speeds, especially 40 km/h.</div>

<div class="mt-6 max-w-3xl text-xl leading-snug text-slate-300">A road operator would also need an agreed response when the system cannot recommend a limit.</div>

<div class="absolute bottom-14 left-14 right-14">
  <div class="border-t-4 border-dashed border-amber-300 mb-5"></div>
  <div class="text-2xl font-bold">Thank you. Questions?</div>
</div>