#!/bin/bash

if [ ! -d "gh-docs" ]; then
  git clone https://github.com/github/docs gh-docs
  cd gh-docs
  git checkout f2fc65ba97
fi

if [ ! -d "gh-docs-2026-02-19" ]; then
  unzip resources/gh-docs-2026-02-19.zip -d gh-docs-2026-02-19
fi

uv sync
