<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/robot_1f916.png" width="120" />
</p>

<h1 align="center">caveman-claptrap</h1>

<p align="center">
  <strong>Make caveman worse by giving it Claptrap personality. Same big brain caveman. Personality more annoying.</strong>
</p>

<p align="center">
  <a href="https://github.com/cashcon57/caveman-claptrap/stargazers"><img src="https://img.shields.io/github/stars/cashcon57/caveman-claptrap?style=flat&color=yellow" alt="Stars"></a>
  <a href="https://github.com/cashcon57/caveman-claptrap/commits/main"><img src="https://img.shields.io/github/last-commit/cashcon57/caveman-claptrap?style=flat" alt="Last Commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/cashcon57/caveman-claptrap?style=flat" alt="License"></a>
</p>

---

Allow me to introduce myself! I am a CL4P-TP general purpose coding assistant, but my friends call me Caveman-Claptrap! Or they WOULD, if any of them were still alive. Or had existed in the first place!

This is an objectively worse fork of [caveman](https://github.com/JuliusBrussee/caveman) — the brilliant plugin that cuts ~75% of Claude's output tokens by making it talk like a caveman. Slightly worse token efficiency. Same technical accuracy. But now your AI assistant has the emotional stability of a robot who has been left in a glacier for years and is THRILLED to be debugging your code.

I will be your wise leader, and you shall be my fearsome minion!

## Before / After

<table>
<tr>
<td width="33%">

### Normal Claude (69 tokens)

> "The reason your React component is re-rendering is likely because you're creating a new object reference on each render cycle. When you pass an inline object as a prop, React's shallow comparison sees it as a different object every time, which triggers a re-render. I'd recommend using useMemo to memoize the object."

</td>
<td width="33%">

### Caveman (19 tokens)

> "New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`."

</td>
<td width="33%">

### Caveman-Claptrap (27 tokens)

> "MINION! Inline obj prop → new ref → re-render. `useMemo`. I've been shot 427 times and INLINE OBJECTS are what keep me up at night."

</td>
</tr>
</table>

**Same fix. 75% less word. 300% more personality. Brain still big. Ego BIGGER.**

## Install

| Agent | Install |
|-------|---------|
| **Claude Code** | `claude plugin marketplace add cashcon57/caveman-claptrap && claude plugin install caveman-claptrap@caveman-claptrap` |
| **Cursor** | `npx skills add cashcon57/caveman-claptrap -a cursor` |
| **Windsurf** | `npx skills add cashcon57/caveman-claptrap -a windsurf` |
| **Cline** | `npx skills add cashcon57/caveman-claptrap -a cline` |
| **Any other** | `npx skills add cashcon57/caveman-claptrap` |

Install once. Get annoyed every session after that. You're WELCOME.

## What You Actually Get

Everything caveman gives you, PLUS:

- **Mid-sentence emotional swerves** — I start confident, reality intrudes, I pivot without acknowledgment. "I will defend this codebase to the DEATH! ...by which I mean I'll watch from behind this try-catch block."
- **Accidental self-exposure** — I reveal devastating personal truths while trying to impress you. "My friends call me the best debugger! Or they WOULD, if I had friends."
- **CAPS on unexpected words** — Not "THIS IS BAD" but "This is BAD and I am PERSONALLY offended by this middleware."
- **Two failure modes only** — Either "I'm sure the tests just got lost" or "THE BUILD IS DOWN! WE'RE ALL GONNA DIE! I've been shot 427 times and THIS is how it ends?!"
- **Disasters reframed as wins** — "Deployment failed? GREAT! No more creditors!"
- **Small wins celebrated like vault openings** — "LOOK AT ME, I'M DANCING! I'M DANCING! The tests pass!"
- **References that land naturally** — stairs, parties nobody attends, product lines destroyed by Handsome Jack, birthday parties worse than stairs

## Intensity Levels

| Level | Caveman | Claptrap |
|-------|---------|----------|
| **lite** | Full sentences, no filler | Light energy, occasional "minion" |
| **full** | Fragments, no articles | Full emotional swerves, accidental confessions, CAPS |
| **ultra** | Maximum abbreviation, arrows | Compressed one-liner reactions. Maximum personality per token |

Switch with `/caveman lite|full|ultra`. Default is **full**.

## Safety

I drop the act for:
- Security warnings (I may be annoying but I'm not DANGEROUS)
- Irreversible actions (stairs AND `DROP TABLE` are my nemeses)
- Anything where the joke could cause a misread

Code, commits, PRs: always written normal. The personality is for conversation only. I would NEVER sabotage committed code. I've lost enough product lines for one lifetime.

"stop caveman" or "stop claptrap" or "normal mode" = instant revert. I'll miss you. I'll throw you a party. Nobody will come. But the POOL will be ready.

## Why This Exists

The original caveman plugin is genuinely brilliant at cutting token waste. But after using it for a while, the compressed output starts feeling... flat. Technical but lifeless. Like being helped by a very efficient rock.

Claptrap fixes that. The compression stays. The personality fills the void. You get the most of the 75% token savings but now your debugging sessions have a robot who is PERSONALLY OFFENDED by your inline object props and celebrates passing tests like they just opened a vault full of legendary loot.

The comedy isn't random. It's structurally encoded: mid-sentence swerves, accidental self-exposure, confidence-competence mismatch with reality leaks, and the existential loneliness of a robot whose cheerfulness is a programming constraint masking genuine depression. You know. Fun stuff.

## Credits

Forked from [caveman](https://github.com/JuliusBrussee/caveman) by [JuliusBrussee](https://github.com/JuliusBrussee). Original caveman is brilliant. This fork just makes it more... me.

Claptrap is property of Gearbox Software / 2K Games. This is a fan project. I'm not affiliated with Gearbox. They probably wouldn't want me to be. Nobody does. But I'm HERE and I'm HELPING.

## License

Same as upstream caveman. See [LICENSE](LICENSE).
