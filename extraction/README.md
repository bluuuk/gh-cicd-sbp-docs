

```
❯ fd -g "*.md" -x basename | sort | uniq -c | sort -nr | head -n 10
 656 index.md
  84 README.md
  17 quickstart.md
   7 guides.md
   5 secrets.md
   4 orgs.md
   4 custom-properties.md
   4 comments.md
   4 best-practices.md
   4 attestations.md
```

index.md is always empty in the sense that it only contains the frontmatter (yaml)

```
❯ fd -g "*.md" -E "index.md" | wc -l
     199
❯ fd -g "*.md" -E "index.md" | shuf -n 20 > ../../../extraction/experiments/05.02/files
```

Use `"runArgs": ["--network=host"]`, as there are ufw firewall rules (apparently form the university) which actually disallows `host.internal.docker`:()


use `"justMyCode": false` in the debugger to also use it for packages!