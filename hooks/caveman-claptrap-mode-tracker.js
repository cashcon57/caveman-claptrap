#!/usr/bin/env node
// caveman-claptrap — UserPromptSubmit hook to track which mode is active
// Inspects user input for /claptrap or /caveman commands and writes mode to flag file

const fs = require('fs');
const path = require('path');
const os = require('os');
const { getDefaultMode } = require('./caveman-claptrap-config');

const flagPath = path.join(os.homedir(), '.claude', '.caveman-claptrap-active');

let input = '';
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const prompt = (data.prompt || '').trim().toLowerCase();

    // Match /claptrap and legacy /caveman commands.
    if (prompt.startsWith('/claptrap') || prompt.startsWith('/caveman')) {
      const parts = prompt.split(/\s+/);
      const cmd = parts[0];
      const arg = parts[1] || '';

      let mode = null;

      if (cmd === '/claptrap-commit' || cmd === '/caveman-commit') {
        mode = 'commit';
      } else if (cmd === '/claptrap-review' || cmd === '/caveman-review') {
        mode = 'review';
      } else if (
        cmd === '/claptrap-compress' ||
        cmd === '/claptrap:compress' ||
        cmd === '/claptrap:caveman-claptrap-compress' ||
        cmd === '/caveman-compress' ||
        cmd === '/caveman:compress' ||
        cmd === '/caveman:caveman-claptrap-compress'
      ) {
        mode = 'compress';
      } else if (
        cmd === '/claptrap' ||
        cmd === '/claptrap:caveman-claptrap' ||
        cmd === '/caveman' ||
        cmd === '/caveman:caveman-claptrap'
      ) {
        if (arg === 'lite') mode = 'lite';
        else if (arg === 'ultra') mode = 'ultra';
        else if (arg === 'wenyan-lite') mode = 'wenyan-lite';
        else if (arg === 'wenyan' || arg === 'wenyan-full') mode = 'wenyan';
        else if (arg === 'wenyan-ultra') mode = 'wenyan-ultra';
        else mode = getDefaultMode();
      }

      if (mode && mode !== 'off') {
        fs.mkdirSync(path.dirname(flagPath), { recursive: true });
        fs.writeFileSync(flagPath, mode);
      } else if (mode === 'off') {
        try { fs.unlinkSync(flagPath); } catch (e) {}
      }
    }

    // Detect deactivation — "stop claptrap", "stop caveman", or "normal mode"
    if (/\b(stop claptrap|stop caveman|normal mode)\b/i.test(prompt)) {
      try { fs.unlinkSync(flagPath); } catch (e) {}
    }
  } catch (e) {
    // Silent fail
  }
});
