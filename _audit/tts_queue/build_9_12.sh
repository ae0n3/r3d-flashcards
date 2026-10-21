#!/bin/bash
set -e
cd /c/Users/rakan/flashcards
echo "=== Building lesson 9 ==="
python _audit/build_lesson.py 9 l9_data.py "快上来吧，要开车了"
echo "=== Building lesson 10 ==="
python _audit/build_lesson.py 10 l10_data.py "我听过钢琴协奏曲《黄河》"
echo "=== Building lesson 11 ==="
python _audit/build_lesson.py 11 l11_data.py "我是跟旅游团一起来的"
echo "=== Building lesson 12 ==="
python _audit/build_lesson.py 12 l12_data.py "我的护照你找到了没有"
echo "=== ALL 9-12 BUILT ==="
