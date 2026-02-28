<script setup lang="ts">
import StepFlow from './StepFlow.vue'
</script>

<template>
<div class="home-content">

  <div class="stats-row">
    <div class="stat-item">
      <div class="stat-number">63</div>
      <div class="stat-label">Health Checks</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">2</div>
      <div class="stat-label">Modules</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">108</div>
      <div class="stat-label">Max Points</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">18</div>
      <div class="stat-label">Skills</div>
    </div>
  </div>

  <div class="home-section">
    <h2>How It Works</h2>
    <p class="subtitle">From scan to merge in four steps</p>
    <StepFlow :steps="[
      { icon: '🔍', title: 'Scan', desc: 'Audit against 63 checks' },
      { icon: '📋', title: 'Review', desc: 'Prioritize the backlog' },
      { icon: '🔧', title: 'Fix', desc: 'Parallel agents create PRs' },
      { icon: '🚀', title: 'Merge', desc: 'Land improvements, repeat' },
    ]" />
    <p>GHS follows a simple loop: <strong>scan</strong> to find problems, optionally <strong>sync</strong> to publish findings as GitHub Issues for team visibility, <strong>fix</strong> to create pull requests (with auto-close references), and <strong>merge</strong> to land the improvements. Each cycle raises your health score closer to 100%.</p>
  </div>

  <div class="home-section">
    <h2>Quick Start</h2>
    <p class="subtitle">Up and running in under a minute</p>
    <div class="language-bash vp-adaptive-theme">
      <button title="Copy Code" class="copy"></button>
      <span class="lang">bash</span>
      <pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="color:#6A737D;--shiki-dark:#6A737D"># Clone GHS and open it with Claude Code</span></span>
<span class="line"><span style="color:#6F42C1;--shiki-dark:#B392F0">git</span><span style="color:#032F62;--shiki-dark:#9ECBFF"> clone https://github.com/Atypical-Consulting/GitHubSkills.git</span></span>
<span class="line"><span style="color:#005CC5;--shiki-dark:#79B8FF">cd</span><span style="color:#032F62;--shiki-dark:#9ECBFF"> GitHubSkills</span></span>
<span class="line"><span style="color:#6F42C1;--shiki-dark:#B392F0">claude</span></span></code></pre>
    </div>
    <p>Then simply ask:</p>
    <div class="language- vp-adaptive-theme">
      <pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>scan owner/repo</span></span></code></pre>
    </div>
    <p>That's it. GHS runs 40 core checks plus language-specific modules (.NET and more coming) — and saves a structured backlog of everything that needs attention.</p>
  </div>

  <div class="home-section">
    <h2>What Gets Checked</h2>
    <p class="subtitle">Modular check system — core always runs, language modules activate on detection</p>
    <table>
      <thead>
        <tr>
          <th>Module</th>
          <th>Activation</th>
          <th>Scored Checks</th>
          <th>Max Points</th>
          <th>Weight</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Core</strong></td>
          <td>Always active</td>
          <td>40</td>
          <td>74 pts</td>
          <td>60%</td>
        </tr>
        <tr>
          <td><strong>.NET</strong></td>
          <td>.sln detected</td>
          <td>20</td>
          <td>34 pts</td>
          <td>40%</td>
        </tr>
        <tr>
          <td><strong>Combined</strong></td>
          <td></td>
          <td><strong>60</strong></td>
          <td><strong>108 pts</strong></td>
          <td></td>
        </tr>
      </tbody>
    </table>
    <p><strong>Core</strong> covers universal best practices: README, LICENSE, CI/CD, branch protection, .editorconfig, CODEOWNERS, issue templates, security, and more across 7 categories.</p>
    <p><strong>.NET</strong> adds .NET-specific checks: Directory.Build.props, test projects, nullable reference types, central package management, code coverage, analyzers, SourceLink, and more across 4 categories.</p>
    <p>When a language module is active, scores are combined: <code>core × 60% + language × 40%</code>. More modules coming soon (Python, Node, Go, Rust).</p>
  </div>

  <div class="home-section">
    <h2>Terminal Output Preview</h2>
    <div class="terminal-block">
      <pre><code>## Repository Scan: phmatray/my-dotnet-project

### Core Health Checks

#### Tier 1 — Required
  [PASS] README.md — Found (2.3 KB)
  [PASS] LICENSE — MIT License
  [FAIL] Repository description — Not set
  [PASS] Branch protection — Enabled on main

#### Tier 2 — Recommended
  [PASS] .gitignore — Found
  [PASS] CI/CD workflows — 2 workflows found
  [FAIL] .editorconfig — Not found
  [PASS] CODEOWNERS — Found
  ...

Core Score: 52/74 (70%)

---

### .NET Health Checks

#### Tier 1 — Required
  [PASS] Directory.Build.props — Found
  [PASS] Test Project Exists — 3 test projects

#### Tier 2 — Recommended
  [PASS] Nullable Reference Types — Enabled
  [FAIL] Central Package Management — Not found
  [FAIL] Code Coverage — No coverlet detected
  [PASS] global.json SDK Pinning — net9.0
  ...

.NET Score: 22/34 (65%)

---

### Combined Health Score: 68%
  (core 70% × 60% + .NET 65% × 40%)

  Core:   52/74  ██████░░ (70%)
  .NET:   22/34  █████░░░ (65%)

---

Backlog saved to: backlog/phmatray_my-dotnet-project/
  health/   — 6 items (5 FAIL, 1 WARN)
  dotnet/   — 3 items (3 FAIL)
  issues/   — 5 items</code></pre>
    </div>
  </div>

</div>
</template>

<style scoped>
.home-content {
  max-width: 1152px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Terminal block */
.terminal-block {
  background-color: #1a1b26;
  border: 1px solid #2d2d3d;
  border-radius: 8px;
  overflow: auto;
}

.terminal-block::before {
  content: '\25CF  \25CF  \25CF';
  display: block;
  padding: 8px 12px 4px;
  font-size: 10px;
  color: #666;
  letter-spacing: 2px;
}

.terminal-block pre {
  margin: 0;
  padding: 0 16px 16px;
  background: transparent;
  overflow-x: auto;
}

.terminal-block code {
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
  line-height: 1.6;
  color: #a9b1d6;
  white-space: pre;
}

/* Table in home content */
.home-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  border-radius: 8px;
  overflow: hidden;
}

.home-content th {
  background: var(--vp-c-bg-soft);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.5px;
  padding: 10px 16px;
  text-align: left;
  border-bottom: 1px solid var(--vp-c-divider);
}

.home-content td {
  padding: 10px 16px;
  border-bottom: 1px solid var(--vp-c-divider);
}

.home-content tr:nth-child(even) {
  background: var(--vp-c-bg-soft);
}

.home-content tr:hover {
  background: var(--vp-c-brand-soft);
}

/* Code blocks in home content */
.home-content .language-bash,
.home-content .language- {
  border-radius: 8px;
  margin: 16px 0;
}

.home-content .language-bash {
  background-color: #1a1b26 !important;
  border: 1px solid #2d2d3d;
}

.home-content .language-bash::before {
  content: '\25CF  \25CF  \25CF';
  display: block;
  padding: 8px 12px 4px;
  font-size: 10px;
  color: #666;
  letter-spacing: 2px;
}
</style>
