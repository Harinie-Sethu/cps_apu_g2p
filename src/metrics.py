# src/metrics.py

def levenshtein(ref, hyp):
    """Edit‐distance between two token lists."""
    n, m = len(ref), len(hyp)
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1):
        dp[i][0] = i
    for j in range(m+1):
        dp[0][j] = j

    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = 0 if ref[i-1] == hyp[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # deletion
                dp[i][j-1] + 1,      # insertion
                dp[i-1][j-1] + cost  # substitution
            )
    return dp[n][m]

def phoneme_error_rate(references, hypotheses):
    """PER = total_edits / total_ref_tokens."""
    total_edits = sum(levenshtein(r, h) for r, h in zip(references, hypotheses))
    total_ref   = sum(len(r) for r in references)
    return (total_edits/total_ref) if total_ref else 0.0

def top1_accuracy(references, hypotheses):
    """Exact‐match rate (lists of IPA tokens)."""
    correct = sum(1 for r,h in zip(references, hypotheses) if r == h)
    return correct / len(references)
