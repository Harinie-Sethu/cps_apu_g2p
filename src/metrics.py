# src/metrics.py

def levenshtein(ref, hyp):
    """Basic DP edit-distance between two lists of tokens."""
    n, m = len(ref), len(hyp)
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1):
        dp[i][0], dp[0][i] = i, i
    for i in range(1,n+1):
        for j in range(1,m+1):
            cost = 0 if ref[i-1]==hyp[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j]+1,    # deletion
                dp[i][j-1]+1,    # insertion
                dp[i-1][j-1]+cost
            )
    return dp[n][m]

def phoneme_error_rate(references, hypotheses):
    """PER = total_edit_distance / total_ref_phonemes"""
    total_edits = sum(levenshtein(r,h) for r,h in zip(references,hypotheses))
    total_phns  = sum(len(r) for r in references)
    return total_edits/total_phns if total_phns else 0.0

def top1_accuracy(references, hypotheses):
    """Exact match rate over the word list."""
    correct = sum(1 for r,h in zip(references,hypotheses) if r==h)
    return correct/len(references)
