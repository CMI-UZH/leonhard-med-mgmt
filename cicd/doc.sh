#!/bin/bash
#
# Code documentation manager

# Print help instructions
if [[ $1 == "--help" || $1 == '-h' ]]; then
  echo "-------------- CODE DOCUMENTATION ---------------"
  echo "Build the project documentation:"
  echo "   source cicd/doc.sh build"
  echo ""
  echo "Clean the project documentation:"
  echo "   source cicd/doc.sh clean"
fi

# Build the project documentation and open it in a browser
if [[ $1 == "run" ]]; then
  make -C docs html
  open docs/build/html/index.html
fi

# Clean up the project documentation for rebuilding (deletes all autosummary files)
if [[ $1 == "clean" ]]; then
  make -C docs clean
  find docs -name "**clusty**" -execdir pwd \; | xargs rm -rf
fi
