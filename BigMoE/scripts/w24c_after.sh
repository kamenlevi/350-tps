#!/bin/bash
# W24c's start gate (the orchestrator 23:0x: "W24c goes first tonight ... as soon as Kamen has been idle for 10 minutes ...
# with memory free ... no start after 00:50"; NewIdeas 23:06-23:07: keep the board's no-chat check): exit 0 once nobody
# has touched the keyboard or mouse for 10 min and no chat process of Kamen's above 2 GB is loaded. Memory is turn45's
# WAITMEM (NO-SWAP >= 29 GB, then PEAK + MARGIN after the grant); the 00:50 cutoff is turn45's NOTAFTER plus w24c.sh's
# own start check. (22:3x version: after Leap's done-files / the chain's fallbacks; dropped on the order above.)
idle=$(ioreg -c IOHIDSystem | awk '/HIDIdleTime/ {print int($NF / 1000000000); exit}')
[ "${idle:-0}" -ge 600 ] || exit 1
ps -axo rss=,command= | awk '/[c]hat\.py|[s]erve\.py/ && $1 > 2097152 {f = 1} END {exit f}'
