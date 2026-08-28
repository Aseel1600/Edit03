# 🎬 Kids Cartoon Factory — Production Status

**Format:** 720×1280 (9:16 vertical) • 24fps • ~45s each • H.264+AAC (~2.5MB/video)
**Voice:** voice-00 (warm female narrator, SAME voice for all 30 videos)
**Structure:** 2 scenes per video (hook/problem → resolution/moral) + animated title card
**NOTE:** Turn 3 reset wiped untracked files once — all assets are now git-tracked & committed every turn.

## Status: ⬜ pending · 🖼️ hero done · 🎬 fully done (scenes + render)

| # | Video | Moral | Status |
|---|-------|-------|--------|
| v01 | Kibo's First Day! | Being brave is easier when you smile and say hello | 🎬 DONE |
| v02 | Momo Can't Sleep! | When you can't sleep, count the twinkling stars | 🎬 DONE |
| v03 | Pip's Big Splash! | Be brave, take one small step | 🎬 DONE |
| v04 | The Littlest Roar! | You don't have to be big to be brave | 🎬 DONE |
| v05 | The Rainbow Carrot! | Sharing makes happy feelings bigger | 🎬 DONE |
| v06 | Polo's Brave Slide! | Scariest things can become your favorite things | 🎬 DONE |
| v07 | Fly Away Balloon! | Good friends make everything right again | 🎬 DONE |
| v08 | A Hug for Poke! | Everybody deserves love, kindness finds a way | 🎬 DONE |
| v09 | Ollie's Lost Treasure! | Friends help friends | 🎬 DONE |
| v10 | Gigi Reaches High! | When we help each other, we can reach anything | 🎬 DONE |
| v11 | Timo's Slow Race! | Slow and steady, never give up | 🎙️ audio ✅ |
| v12 | Nova the Night Owl! | The dark is full of friendly little lights | 🎙️ audio ✅ |
| v13 | Barni's Honey Pot! | A shared treat is the sweetest treat | 🎙️ audio ✅ |
| v14 | Finni and the Fallen Star! | Helping someone makes your kindness shine | 🎙️ audio ✅ |
| v15 | Dolly's Big Jump! | Practice makes progress, keep trying | 🎙️ audio ✅ |
| v16 | Kiki Climbs High! | If you fall, try again | 🎙️ audio ✅ |
| v17 | Hazel's Muddy Day! | Play hard, then scrub-a-dub clean | 🎙️ audio ✅ |
| v18 | Dot's Hide-and-Seek! | Making your friends smile wins every time | 🎙️ audio ✅ |
| v19 | Rocky Says Sorry! | Saying sorry fixes friendships | 🎙️ audio ✅ |
| v20 | Willa's Little Song! | Your voice matters | 🎙️ audio ✅ |
| v21–v30 | Batch 3 (10 new stories) | — | ⬜ |

## Turn plan (quotas: 10 images + 10 voice clips per turn)
- ✅ Turn 3 (this): rebuilt pipeline, 10 heroes + 10 narrations re-banked, committed
- Turn 4: scene 2 ×10 → render v01–v10 (BATCH 1 COMPLETE 🎉) + batch-2 narrations
- Turn 5: batch-2 heroes + batch-3 narrations
- Turn 6: batch-2 scene 2 ×10 → render v11–v20 (BATCH 2 COMPLETE) + batch-3 heroes
- Turn 7: batch-3 scene 2 ×10 → render v21–v30 (ALL 30 🎉)
- Turn 8: INDEX catalog, thumbnail pack, storage housekeeping

## Pipeline
1. `specs_batch*.json` — story bible (hero_prompt, second_prompt, script)
2. `images/vXX_s1.jpg` hero → `images/vXX_s2.jpg` (uses s1 as character reference)
3. `audio/vXX.mp3` — narration (voice-00)
4. `python3 render.py` → `videos/vXX_slug.mp4`
