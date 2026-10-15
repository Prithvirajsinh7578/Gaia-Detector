<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

- Keep detection input and result state in the reusable detection workspace, separate from the page shell, so all modes share cancellation and stale-result handling.
- Configure only verified same-origin detection endpoints in the detection adapter; missing services must fail explicitly rather than use heuristic or fabricated results.
- Keep upload limits as client preflight rules, not claims of provider support; reconcile them with a real provider when one is connected.
