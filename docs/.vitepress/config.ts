import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(
  defineConfig({
    title: 'GHS — GitHub Skills',
    description: 'Claude Code skills for auditing, managing, and improving GitHub repositories',

    head: [
      ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
    ],

    themeConfig: {
      logo: '/logo.svg',

      nav: [
        { text: 'Home', link: '/' },
        { text: 'Getting Started', link: '/getting-started/installation' },
        { text: 'Skills', link: '/skills/' },
        { text: 'Checks', link: '/checks/' },
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
              { text: 'ghs-backlog-board', link: '/skills/ghs-backlog-board' },
              { text: 'ghs-backlog-fix', link: '/skills/ghs-backlog-fix' },
              { text: 'ghs-backlog-score', link: '/skills/ghs-backlog-score' },
              { text: 'ghs-backlog-next', link: '/skills/ghs-backlog-next' },
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
            text: 'Actions',
            items: [
              { text: 'ghs-merge-prs', link: '/skills/ghs-merge-prs' },
            ],
          },
        ],
        '/checks/': [
          {
            text: 'Check Registry',
            items: [
              { text: 'Overview', link: '/checks/' },
              { text: 'Tier 1 — Required', link: '/checks/tier-1' },
              { text: 'Tier 2 — Recommended', link: '/checks/tier-2' },
              { text: 'Tier 3 — Nice to Have', link: '/checks/tier-3' },
            ],
          },
        ],
        '/workflows/': [
          {
            text: 'Workflow Guides',
            items: [
              { text: 'Health Loop', link: '/workflows/health-loop' },
              { text: 'Issue Loop', link: '/workflows/issue-loop' },
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
              { text: 'Backlog Format', link: '/reference/backlog-format' },
              { text: 'Agent Contract', link: '/reference/agent-contract' },
              { text: 'Check Format', link: '/reference/check-format' },
              { text: 'Scoring', link: '/reference/scoring' },
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
        copyright: 'Copyright © 2024-present Atypical Consulting',
      },
    },

    mermaid: {},
  })
)
