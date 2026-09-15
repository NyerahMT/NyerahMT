<div align="center">

<img src="https://raw.githubusercontent.com/NyerahMT/NyerahMT/main/assets/profile-hero.svg" width="100%" alt="Matthew Talafous — real-time simulation, iOS porting, and mechanical systems" />

<br>

**Mechanical TIG welder · Independent developer · NyerahWorks**

I build and port software where **physics, rendering, platform architecture, and real hardware behavior** meet.

<br>

<a href="https://github.com/NyerahMT/Critical-State"><img src="https://img.shields.io/badge/Critical_State-active-22c55e?style=flat-square" alt="Critical State active" /></a>
<a href="https://github.com/NyerahMT/rigs-of-rods-ios"><img src="https://img.shields.io/badge/Rigs_of_Rods-iOS_port-38bdf8?style=flat-square" alt="Rigs of Rods iOS port" /></a>
<a href="https://github.com/NyerahMT/principia-ios"><img src="https://img.shields.io/badge/Principia-iOS_port-2563eb?style=flat-square" alt="Principia iOS port" /></a>
<a href="https://github.com/NyerahMT/engine-sim-ios"><img src="https://img.shields.io/badge/Engine_Simulator-iOS_port-6366f1?style=flat-square" alt="Engine Simulator iOS port" /></a>

</div>

---

## What I build

Most of my work lives in the part of software where abstractions stop being clean.

I work on **real-time simulation, desktop-to-mobile ports, graphics, input systems, performance, and platform integration** — especially software that represents something physical: vehicles, engines, machines, fluids, reactors, or other coupled systems.

My mechanical background strongly influences how I approach software. I care about causality, constraints, failure modes, instrumentation, and whether a system behaves for the right reason instead of merely producing the right-looking output.

```text
physical system  →  model  →  solver  →  platform  →  rendering / input  →  user
      ↑                                                               ↓
      └──────────────────── observe, test, refine ────────────────────┘
```

---

## Selected work

<table>
<tr>
<td width="50%" valign="top">

<h3>⚛️ Critical State</h3>

<strong>Coupled nuclear power-plant simulation game</strong>

A mobile-first reduced-order PWR simulator built as a connected physical system rather than a collection of scripted gauges. The model couples reactor kinetics, thermal response, primary hydraulics, steam generation, turbine-generator dynamics, condenser behavior, feedwater, protection, equipment condition, and plant economics.

<code>Kotlin</code> <code>Real-time simulation</code> <code>Thermodynamics</code> <code>Systems modeling</code>

<br><br>
<a href="https://github.com/NyerahMT/Critical-State"><strong>View project →</strong></a>

</td>
<td width="50%" valign="top">

<h3>🚙 Rigs of Rods iOS</h3>

<strong>iOS port of the open-source soft-body vehicle simulator</strong>

Current porting work on a large C++ simulation codebase with a much wider surface area than a typical mobile app: rendering, input, filesystem assumptions, platform dependencies, content loading, and the existing vehicle/terrain ecosystem all have to survive the move to iOS.

<code>C++</code> <code>iOS</code> <code>OGRE</code> <code>Porting</code> <code>Soft-body physics</code>

<br><br>
<a href="https://github.com/NyerahMT/rigs-of-rods-ios"><strong>View project →</strong></a>

</td>
</tr>
<tr>
<td width="50%" valign="top">

<h3>⚙️ Principia iOS</h3>

<strong>Physics sandbox / engineering simulator port</strong>

An iOS adaptation of Principia, a sandbox built around rigid-body mechanics, electronics, robotics, sensors, logic, scripting, and user-built machinery. The port focuses on keeping the upstream architecture recognizable while handling iOS lifecycle, touch input, filesystem behavior, UI scaling, rendering, and performance.

<code>C++</code> <code>OpenGL ES</code> <code>Touch input</code> <code>Lifecycle</code> <code>Platform integration</code>

<br><br>
<a href="https://github.com/NyerahMT/principia-ios"><strong>View project →</strong></a>

</td>
<td width="50%" valign="top">

<h3>🔥 Engine Simulator iOS</h3>

<strong>Real-time combustion engine simulation on iOS</strong>

An iOS adaptation of Engine Simulator, bringing its real-time crankshaft, combustion, airflow, valvetrain, ignition, and procedural audio simulation onto mobile while preserving the character of the original desktop project.

<code>C++</code> <code>iOS</code> <code>Rendering</code> <code>Audio</code> <code>Performance</code>

<br><br>
<a href="https://github.com/NyerahMT/engine-sim-ios"><strong>View project →</strong></a>

</td>
</tr>
</table>

---

## Technical range

<table>
<tr>
<td width="33%" valign="top">

### Simulation

- Real-time physical systems
- Mechanical / vehicle simulation
- Engine and power-system models
- Thermal-fluid behavior
- Coupled subsystem architecture
- Numerical stability and time stepping

</td>
<td width="33%" valign="top">

### Platform

- C++ desktop → iOS ports
- Application lifecycle
- Touch / controller input
- Filesystem and asset loading
- Dependency adaptation
- Build and CI plumbing

</td>
<td width="33%" valign="top">

### Graphics + compute

- OpenGL / OpenGL ES
- Metal
- GPU compute
- Real-time rendering
- Performance debugging
- Swift concurrency / GCD

</td>
</tr>
</table>

<div align="center">

<img src="https://skillicons.dev/icons?i=cpp,swift,kotlin,python,lua,git,github&theme=dark" alt="C++, Swift, Kotlin, Python, Lua, Git and GitHub" />

<br><br>

<code>C++</code> · <code>Swift</code> · <code>Kotlin</code> · <code>Metal</code> · <code>OpenGL / ES</code> · <code>Python</code> · <code>Lua</code>

</div>

---

## Smaller systems & experiments

**[Fluid Engine Swift](https://github.com/NyerahMT/fluid-engine-swift)** — restored an older Swift / Metal fluid simulator using GPU compute and Grand Central Dispatch.

**[Full Authority](https://github.com/NyerahMT/Full-Authority)** — archived flight-simulation prototype exploring realistic aircraft behavior, atmospheric effects, rendering, and mobile controls. Its experimentation ultimately fed into later simulation and porting work.

---

## Repository activity

I care more about useful engineering than contribution-calendar cosmetics, but the profile repo still tracks some live development history automatically.

<details>
<summary><strong>Show live development activity</strong></summary>
<br>

<!-- AUTO-STATS:START -->
<div align="center">

<img
src="https://raw.githubusercontent.com/NyerahMT/NyerahMT/main/assets/development-activity.svg"
width="720"
/>

</div>

| Port | Commits ahead | GitHub attributed |
|:---|---:|---:|
| **Principia iOS** | 33 | 33 |
| **Fluid Engine Swift** | 23 | 2 |
| **Rigs of Rods iOS** | 0 | 0 |
| **Total** | **56** | **35** |

<sub>
"Commits ahead" measures development currently added beyond upstream.
"GitHub attributed" counts commits GitHub directly associates with my account.
The two metrics overlap.
</sub>
<!-- AUTO-STATS:END -->

</details>

---

<div align="center">

### Build the model. Find the failure. Make it behave.

<sub>Mechanical systems · simulation · iOS porting</sub>

</div>
