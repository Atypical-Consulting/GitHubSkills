import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(
  defineConfig({
    title: 'GHS — GitHub Skills',
    description: 'Claude Code skills for auditing, managing, and improving GitHub repositories',
    base: '/GitHubSkills/',
    lastUpdated: true,

    head: [
      ['link', { rel: 'icon', type: 'image/svg+xml', href: '/GitHubSkills/logo.svg' }],
      ['meta', { property: 'og:type', content: 'website' }],
      ['meta', { property: 'og:title', content: 'GHS — GitHub Skills' }],
      ['meta', { property: 'og:description', content: '63 health checks, modular scoring, parallel AI agents, real pull requests. Claude Code skills for auditing and improving GitHub repositories.' }],
      ['meta', { property: 'og:url', content: 'https://atypical-consulting.github.io/GitHubSkills/' }],
      ['meta', { name: 'twitter:card', content: 'summary' }],
      ['meta', { name: 'twitter:title', content: 'GHS — GitHub Skills' }],
      ['meta', { name: 'twitter:description', content: '63 health checks, modular scoring, parallel AI agents, real pull requests. Claude Code skills for auditing and improving GitHub repositories.' }],
    ],

    themeConfig: {
      logo: '/logo.svg',
      outline: [2, 3],

      nav: [
        { text: 'Home', link: '/' },
        { text: 'Getting Started', link: '/getting-started/installation' },
        { text: 'Skills', link: '/skills/' },
        { text: 'Checks', link: '/checks/' },
        { text: 'Workflows', link: '/workflows/health-loop' },
        { text: 'Reference', link: '/reference/scoring' },
        { text: 'Contributing', link: '/contributing/' },
      ],

      sidebar: {
        '/getting-started/': [
          {
            text: 'Getting Started',
            items: [
              { text: 'Installation', link: '/getting-started/installation' },
              { text: 'Your First Scan', link: '/getting-started/first-scan' },
              { text: 'Core Concepts', link: '/getting-started/concepts' },
              { text: 'Troubleshooting', link: '/getting-started/troubleshooting' },
            ],
          },
        ],
        '/skills/': [
          {
            text: 'Skills Reference',
            items: [
              { text: 'Overview', link: '/skills/' },
            ],
          },
          {
            text: 'Health Loop',
            items: [
              { text: 'ghs-repo-scan', link: '/skills/ghs-repo-scan' },
              { text: 'ghs-backlog-sync', link: '/skills/ghs-backlog-sync' },
              { text: 'ghs-backlog-board', link: '/skills/ghs-backlog-board' },
              { text: 'ghs-backlog-fix', link: '/skills/ghs-backlog-fix' },
              { text: 'ghs-backlog-score', link: '/skills/ghs-backlog-score' },
              { text: 'ghs-backlog-next', link: '/skills/ghs-backlog-next' },
            ],
          },
          {
            text: 'Profile',
            items: [
              { text: 'ghs-profile', link: '/skills/ghs-profile' },
            ],
          },
          {
            text: 'Issue Loop',
            items: [
              { text: 'ghs-issue-triage', link: '/skills/ghs-issue-triage' },
              { text: 'ghs-issue-analyze', link: '/skills/ghs-issue-analyze' },
              { text: 'ghs-issue-implement', link: '/skills/ghs-issue-implement' },
            ],
          },
          {
            text: 'Code Review & Release',
            items: [
              { text: 'ghs-review-pr', link: '/skills/ghs-review-pr' },
              { text: 'ghs-release', link: '/skills/ghs-release' },
            ],
          },
          {
            text: 'Repository Setup',
            items: [
              { text: 'ghs-project-init', link: '/skills/ghs-project-init' },
            ],
          },
          {
            text: 'Actions',
            items: [
              { text: 'ghs-action-fix', link: '/skills/ghs-action-fix' },
              { text: 'ghs-merge-prs', link: '/skills/ghs-merge-prs' },
            ],
          },
          {
            text: 'Orchestration',
            items: [
              { text: 'ghs-orchestrate', link: '/skills/ghs-orchestrate' },
              { text: 'ghs-dev-loop', link: '/skills/ghs-dev-loop' },
            ],
          },
          {
            text: 'Utilities',
            items: [
              { text: 'ghs-repos-pull', link: '/skills/ghs-repos-pull' },
            ],
          },
        ],
        '/checks/': [
          {
            text: 'Check Registry',
            items: [
              { text: 'Overview', link: '/checks/' },
            ],
          },
          {
            text: 'Core Module',
            items: [
              { text: 'Tier 1 — Required', link: '/checks/tier-1' },
              { text: 'Tier 2 — Recommended', link: '/checks/tier-2' },
              { text: 'Tier 3 — Nice to Have', link: '/checks/tier-3' },
            ],
          },
          {
            text: '.NET Module',
            items: [
              { text: 'Tier 1 — Required', link: '/checks/dotnet-tier-1' },
              { text: 'Tier 2 — Recommended', link: '/checks/dotnet-tier-2' },
              { text: 'Tier 3 — Nice to Have', link: '/checks/dotnet-tier-3' },
            ],
          },
        ],
        '/workflows/': [
          {
            text: 'Workflow Guides',
            items: [
              { text: 'Health Loop', link: '/workflows/health-loop' },
              { text: 'Issue Loop', link: '/workflows/issue-loop' },
              { text: 'Orchestration', link: '/workflows/orchestration' },
            ],
          },
        ],
        '/contributing/': [
          {
            text: 'Contributing',
            items: [
              { text: 'Overview', link: '/contributing/' },
              { text: 'Adding a Check', link: '/contributing/adding-a-check' },
              { text: 'Adding a Skill', link: '/contributing/adding-a-skill' },
              { text: 'Conventions', link: '/contributing/conventions' },
            ],
          },
        ],
        '/reference/': [
          {
            text: 'Reference',
            items: [
              { text: 'Scoring', link: '/reference/scoring' },
              { text: 'GitHub Projects Format', link: '/reference/backlog-format' },
              { text: 'Check Format', link: '/reference/check-format' },
              { text: 'Agent Contract', link: '/reference/agent-contract' },
            ],
          },
        ],
      },

      socialLinks: [
        { icon: 'github', link: 'https://github.com/Atypical-Consulting/GitHubSkills' },
      ],

      search: {
        provider: 'local',
      },

      editLink: {
        pattern: 'https://github.com/Atypical-Consulting/GitHubSkills/edit/main/docs/:path',
        text: 'Edit this page on GitHub',
      },

      footer: {
        message: 'Released under the MIT License.',
        copyright: 'Copyright © 2026-present Atypical Consulting',
      },
    },

    mermaid: {},
  })
)
