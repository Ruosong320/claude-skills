# claude-skills

我的 Claude Code skills 集合，同时作为 darwin-skill 自动优化的**棘轮仓库**：
每个 kept 改动进 main，被 judge 判 worse 的改动回滚，历史全程可追溯。

## 目录

每个子目录是一个 skill，入口为 `SKILL.md`。

## 优化流程

由 darwin-skill 驱动：基线评估 → 单维度改进 → 独立 judge 配对盲评 → 多数决 keep/revert。
优化日志见 `darwin-results.tsv`。
