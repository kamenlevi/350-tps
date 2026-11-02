#!/bin/bash
# THE COMBINATION, Tuesday by day (the orchestrator 11-02 21:1x: "turn on, one switch group at a time, with a bitwise check
# after each"; BigMoE = the integrator, the only writer of R57_PRESET=45). One ticket, arms at C 256 in order, each the
# previous + one switch group (cumulative, so each delta is measured on the stack it joins):
#   cmb0 the default (REF2-T, R57_PRESET=45)       -> its tokens = the reference of every later arm (+ chat23 where stored)
#   cmb1 + the chat switch (R57_CHATSW=1)           cmb1c + chat at 8 rows (R57_CHATROWS=8; the orchestrator 21:2x)
#   cmb2 + A6 keep (R57_A6=keep)
#   cmb3 + COPYGATE (R57_COPY=g2)                   cmb4 + D7b on code (R57_D7B=code)
#   cmb5 + JOINT (BIGMOE_JOINT=1)                   cmb6 + K-83 (K83_EXACT=1; its drafter forms stay on the bf16 drafter)
#   FAST: fastBE / fastCE = cmb6 + R57_FAST (EvalSuite's RELAX arms B + E / C + E), tokens not checked
# then variants on cmb4's stack: cmb3t (COPYGATE with the drafter's own t cut) and cmb32 (R57_ROWS=32, MATCH 2.5's rule),
# and cmbsc on cmb6's: the sidecar x1.5 at equal pool bytes (data/seed45/laysz45_256_sc15.json, md5 5d6d6ec0; replay
# 11-02: reads per check -7..-25 %, MB code no-gate +4.6 %, chat -0.4..-3.3 %; exact: pool sizes only).
# A lever whose arm differs in any token, or that does not speed up the stack, stays off (the arm list is edited before
# arming, from the night's verdicts). Prompts: code x4 (HumanEval 68 / 91 / 16 / 6), math, chat x4, agent x2; CAP 256.
# Shared GPU by day: rough deltas; the quiet measurement of the combined default runs first each night from 00:30
# (NewIdeas' GPU order 11-02 21:3x), Wed before FLOOR.
# usage: inside turn45 (HAVE_LOCK=1 KEEP_LOCK=1), with frozen copies (data/r57/snap/*_cmb.*) like the night's
export PATH="$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
cd "$HOME/BigMoE" || exit 1
mkdir -p data/cmb
LOG="$HOME/BigMoE/data/cmb/cmb.log"
say() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$LOG"; }
RUN="/bin/bash data/r57/snap/c45_runner_cmb.sh"
export C45_SCREEN=data/r57/snap/r57_screen_cmb.py C45_DEADLINE=${CMB_DEADLINE:-1420} C45_OUT="$HOME/BigMoE/data/cmb"
KEYS="humaneval/HumanEval/68,humaneval/HumanEval/91,humaneval/HumanEval/16,humaneval/HumanEval/6"
KEYS="$KEYS,math500/test/prealgebra/1640.json,ifeval/1220,ifeval/1561,multi/de3,multi/zh15,agent/bash18,agent/text23"
S1="R57_CHATSW=1"; S1C="$S1,R57_CHATROWS=8"; S2="$S1C,R57_A6=keep"; S3="$S2,R57_COPY=g2"; S4="$S3,R57_D7B=code"; S5="$S4,BIGMOE_JOINT=1"
S6="$S5,K83_EXACT=1"
say "combination start (pid $$, HAVE_LOCK=$HAVE_LOCK)"
R57_KEYS=$KEYS MG=6 C45_ALARM=900 C45_REFTOK="$HOME/BigMoE/data/r57/chat23_ref_tokens.json:gate+t" C45_ARMS="cmb0_256:256" $RUN
say "cmb0 (the default) rc=$?"
REF0="$HOME/BigMoE/data/r57/cmb0_256_tokens.json:gate+t"   # the default's own tokens: every later arm against them
[ -s "${REF0%%:*}" ] || { say "no cmb0 tokens: stop"; exit 1; }
R57_KEYS=$KEYS MG=6 C45_ALARM=900 C45_REFTOK=$REF0 C45_ARMS="${CMB_ARMS:-cmb1_256:256:$S1 cmb1c_256:256:$S1C cmb2_256:256:$S2 cmb3_256:256:$S3 cmb4_256:256:$S4 cmb5_256:256:$S5 cmb6_256:256:$S6 cmb3t_256:256:$S4,R57_COPY=g2t cmb32_256:256:$S4,R57_ROWS=32 cmbsc_256:256:$S6,BIGMOE_TIER_SIZES=$HOME/BigMoE/data/seed45/laysz45_256_sc15.json}" $RUN
say "arms rc=$?"
# the FAST preset (Kamen 21:31: two first-class tracks): EvalSuite's RELAX rules on the full exact stack, per prompt set as
# its arms B + E (code mode: gate 0.99 + copy gate + the comment loophole; chat R1) and C + E (+ R1 on code / math);
# quality-defined, so no REF2-T token check (EvalSuite's same-scores test judges them): tok/s, kept and the gated share
R57_KEYS=$KEYS MG=6 C45_ALARM=900 C45_ARMS="${CMB_FAST:-fastBE_256:256:$S6,R57_FAST=BE,R57_REFTOK= fastCE_256:256:$S6,R57_FAST=CE,R57_REFTOK=}" $RUN
say "FAST arms rc=$?"
"$HOME/BigMoE/.venv/bin/python" scripts/combo_report.py >> "$LOG" 2>&1; say "report rc=$? (data/cmb/combo_report.txt)"
say "combination end"
