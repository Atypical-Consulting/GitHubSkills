<script setup lang="ts">
import StepFlow from './StepFlow.vue'
</script>

<template>
<div class="home-content">

  <div class="stats-row">
    <div class="stat-item">
      <div class="stat-number">38</div>
      <div class="stat-label">Health Checks</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">10</div>
      <div class="stat-label">Skills</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">67</div>
      <div class="stat-label">Max Score</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">3</div>
      <div class="stat-label">Tiers</div>
    </div>
  </div>

  <div class="home-section">
    <h2>How It Works</h2>
    <p class="subtitle">From scan to merge in four steps</p>
    <StepFlow :steps="[
      { icon: '🔍', title: 'Scan', desc: 'Audit against 38 checks' },
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
    <p>That's it. GHS runs 38 health checks across documentation, settings, CI/CD, security, and community standards — and saves a structured backlog of everything that needs attention.</p>
  </div>

  <div class="home-section">
    <h2>What Gets Checked</h2>
    <p class="subtitle">35 scored checks across 3 tiers, plus 3 informational</p>
    <table>
      <thead>
        <tr>
          <th>Tier</th>
          <th>Focus</th>
          <th>Checks</th>
          <th>Points Each</th>
          <th>Subtotal</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Tier 1 — Required</strong></td>
          <td>Fundamental repo quality</td>
          <td>4</td>
          <td>4 pts</td>
          <td>16 pts</td>
        </tr>
        <tr>
          <td><strong>Tier 2 — Recommended</strong></td>
          <td>Professional standards</td>
          <td>20</td>
          <td>2 pts</td>
          <td>40 pts</td>
        </tr>
        <tr>
          <td><strong>Tier 3 — Nice to Have</strong></td>
          <td>11 scored + 3 INFO</td>
          <td>—</td>
          <td>1 pt</td>
          <td>11 pts</td>
        </tr>
        <tr>
          <td><strong>Total</strong></td>
          <td></td>
          <td><strong>35 scored</strong></td>
          <td></td>
          <td><strong>67 pts</strong></td>
        </tr>
      </tbody>
    </table>
    <p><strong>Tier 1</strong> covers the essentials every repo needs: README, LICENSE, repository description, and branch protection.</p>
    <p><strong>Tier 2</strong> covers professional standards: .gitignore, CI/CD workflows, .editorconfig, CODEOWNERS, issue templates, PR template, topics, changelog, GitHub releases, stale issue/PR/branch detection, merge strategy, and README content quality.</p>
    <p><strong>Tier 3</strong> adds polish: SECURITY.md, CONTRIBUTING.md, security alerts, .editorconfig drift, code of conduct, homepage URL, .gitattributes, version pinning, dependency update config, README table of contents, and README license mention.</p>
  </div>

  <div class="home-section">
    <h2>Terminal Output Preview</h2>
    <div class="terminal-block">
      <pre><code>Repository Health: phmatray/my-project
Score: 45/67 (67%) ██████░░

Tier 1 — Required (4 checks)
  [PASS] README exists
  [PASS] LICENSE exists
  [FAIL] Repository description is empty
  [PASS] Branch protection enabled

Tier 2 — Recommended (20 checks)
  [PASS] .gitignore exists
  [FAIL] No CI/CD workflows found
  [PASS] CI workflow health — all workflows passing
  [FAIL] .editorconfig not found
  [PASS] CODEOWNERS exists
  [PASS] Issue templates configured
  [FAIL] No PR template found
  [PASS] Repository topics set
  [PASS] CHANGELOG exists
  [PASS] Delete branch on merge enabled
  [PASS] GitHub releases found
  [PASS] No stale issues (&gt; 90 days)
  [PASS] No stale PRs (&gt; 30 days)
  [WARN] Stale branches — 3 branches with no recent activity
  [PASS] Merge strategy configured
  [PASS] README has description section
  [PASS] README has badges
  [PASS] README has installation instructions
  [PASS] README has usage section
  [FAIL] README has no features section

Tier 3 — Nice to Have (14 checks)
  [FAIL] SECURITY.md not found
  [FAIL] CONTRIBUTING.md not found
  [PASS] Security alerts enabled
  [PASS] .editorconfig matches file styles
  [FAIL] No code of conduct
  [PASS] Homepage URL set
  [PASS] .gitattributes exists
  [FAIL] No version pinning (global.json / .tool-versions)
  [PASS] Dependabot or Renovate configured
  [FAIL] README has no table of contents
  [PASS] README mentions license
  [INFO] FUNDING.yml not found (optional)
  [INFO] Discussions not enabled (optional)
  [INFO] Commit signoff not required (optional)

Backlog saved to: backlog/phmatray_my-project/
  health/   — 10 items (9 FAIL, 1 WARN)
  issues/   — 7 items</code></pre>
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
