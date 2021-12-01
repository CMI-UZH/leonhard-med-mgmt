#!/bin/bash
#
# Code coverage CI/CD tool

# Print help instructions
if [[ $1 == "--help" || $1 == '-h' ]]; then
  echo "-------------- COVERAGE REPORTING ---------------"
  echo "Run a coverage report:"
  echo "   source cicd/coverage.sh run"
  echo ""
  echo "Clean a coverage report:"
  echo "   source cicd/coverage.sh clean"
fi

# Run the coverage report and open it in the browser
if [[ $1 == "run" ]]; then
  coverage run -m pytest
  coverage html
  open .htmlcov/index.html
fi

# Clean up the coverage report results
if [[ $1 == "clean" ]]; then
  rm -rf .pytest_cache
  rm -rf .htmlcov
  rm .coverage
fi
