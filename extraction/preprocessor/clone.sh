set -euo pipefail

# This scripts runs on relation to:
# (extraction) root ➜ /workspaces/github-best-pratices/extraction/gh-docs (main) $ git rev-parse HEAD
# cb2c192f5e555103dde189c09cdf9532b0b8aacf
# See changes file for the original repo

outdir="${1:-/workspaces/github-best-pratices/extraction/gh-docs-$(date -I)/content}"
mkdir -p "$outdir"

use_cache=false
if [ $# -ge 1 ]; then
  echo "Using cache directory: $outdir"
  use_cache=true
else
  git clone https://github.com/github/docs "/workspaces/github-best-pratices/extraction/gh-docs"
  echo "Using fresh output directory: $outdir"
fi

cd "/workspaces/github-best-pratices/extraction/gh-docs/content"

if [ "$use_cache" = false ]; then 
  # format will be https://docs.github.com/api/article?pathname=/en/<path> with <path> starting from /content without file extension!
  fdfind -g "*.md" -E "index.md" -E "README.md" -j 1 . \
    -x sh -c '
      echo "File $1"
      url="https://docs.github.com/api/article?pathname=/en/$1"
      clean_path="${1#./}"
      outfile="$2/$clean_path.json"

      mkdir -p "$(dirname "$outfile")"

      if ! curl -fsSL --retry 3 "$url" -o "$outfile" ; then
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] FAILED: $url"
      fi
      sleep 1.1
    ' sh {.} "$outdir"

  # format will be https://docs.github.com/api/article?pathname=/en/<path> with <path> starting from /content without file name and extension!
  fdfind "index.md" -j 1 . \
    -x sh -c '
      fullpath=$(dirname "$1")
      echo "File $1 - $fullpath"
      url="https://docs.github.com/api/article?pathname=/en/$fullpath"
      fullpath=$(dirname "$1")
      clean_path="${fullpath#./}"
      outfile="$2/$clean_path.json"

      mkdir -p "$(dirname "$outfile")"

      if ! curl -fsSL --retry 3 "$url" -o "$outfile" ; then
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] FAILED: $url"
      fi
      sleep 1.1
    ' sh {.} "$outdir"
fi

# preprocess
fdfind -g "*.json" "$outdir" -x sh -c 'bun run /workspaces/github-best-pratices/extraction/preprocessor/index.ts "$1" > "$2.md"' _ {} {.}