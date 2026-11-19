p = 'COORDINATION.md'
s = open(p).read()

# 1. G3b row, inserted before the G3 verification row of the Results table
key = 'Full battery green on the merged tree'
i = s.index(key)
start = s.rindex('\n|', 0, i) + 1          # start of that table row
row = ('| G3b | One wording defect #97 could not have seen, found by reading the published output after the merge: '
       '`pages/executive-summary.html` still read "(7 nights; seven playing days, **checkout the next day**)" - true '
       'while `check_out` held the regression value 2026-12-12, wrong now that it is 2026-12-13. Rewritten from the '
       'data, not from a sentence: "(7 nights; the 7 playing days run December 6, 2026 to December 12, 2026, checking '
       'out the morning after the last one)". | `scripts/build_ea99006a.py` (`build_exec`, one sentence, driven by '
       '`PLAY_END`); grep on the rendered page before and after; 31/31 tests, both link checkers green. |\n')
s = s[:start] + row + s[start:]

# 2. irregularity 8 + publication record, before the Sources paragraph
mark = '**Sources read in this session.**'
j = s.index(mark)
extra = (
    '8. **The daily-scrape workflow pushes onto session branches.** `24e12c9` and `33919e2` ("scrape(251c122f): '
    'daily official-source capture") were committed directly to `arena/6dba9b3c-poker5` while this session worked, '
    'which is what made two plain `git push`es non-fast-forward. Both were **merged**, never overwritten - a force-push '
    'would have discarded a capture. Consequence: never `git push --force` on a branch the scraper can reach; fetch '
    'and merge first. Re-deriving after each capture is now part of the verification loop (the second such merge moved '
    'only 94 `entry_evidence.sheet_retrieved` timestamps, 0 verdicts, 0 values - which is the behaviour G1 was built '
    'to make safe).\n\n'
    '**Publication record (6dba9b3c).** PR https://github.com/karagemop466-tech/Poker5/pull/101 - merged into `main` '
    'as `4c341ee` with `gh pr merge 101 --merge`. CI on the PR: "Quality checks" pass (the run includes the new '
    '`complete_routes_6dba9b3c.py --check` drift guard and the 31/31 suite) and "Validate Dec 2-9 poker dashboard" '
    'pass. GitHub Pages "pages build and deployment" run `44629236826` on `main` completed with `success`; the '
    'deployed tree was then re-read from `origin/main` and checked: `data/ea99006a/routes.json` = 72 pairs, '
    '`pages/routes.html` renders 72 Apple + 72 Google links, `pages/flagged-review.html` carries F70, the planner is '
    'cut at the last playing day, and `meta.trip` reads check_in 2026-12-06 / check_out 2026-12-13 / last_play_day '
    '2026-12-12 / 7 nights. The executive-summary fix (G3b) and this record follow in a second, small PR, because '
    '#101 had already merged when it was found by reading the live output.\n\n')
s = s[:j] + extra + s[j:]
open(p, 'w').write(s)
print('COORDINATION.md updated')
