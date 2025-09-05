#!/bin/bash

echo "🔧 Resolving Git Conflicts..."

# Step 1: Remove cache files that cause conflicts
echo "1. Removing cache files..."
rm -rf __pycache__/

# Step 2: Abort current merge to clean state
echo "2. Aborting current merge..."
git merge --abort 2>/dev/null || echo "No merge to abort"

# Step 3: Set pull strategy
echo "3. Setting pull strategy..."
git config pull.rebase false

# Step 4: Fetch latest changes
echo "4. Fetching latest changes..."
git fetch origin

# Step 5: Try to merge main into current branch
echo "5. Merging main into current branch..."
git merge origin/main

# Check if there are conflicts
if git diff --name-only --diff-filter=U | grep -q .; then
    echo "⚠️  Manual conflict resolution needed for these files:"
    git diff --name-only --diff-filter=U
    
    echo ""
    echo "📝 For each conflicted file, choose our improved version (HEAD):"
    echo "   - Keep pipeline-aligned implementations"
    echo "   - Keep chunked segmentation functions" 
    echo "   - Keep improved JSON parsing and answer generation"
    echo ""
    echo "After resolving conflicts manually, run:"
    echo "   git add ."
    echo "   git commit -m 'Resolve merge conflicts, prioritizing pipeline improvements'"
    echo "   git push origin cursor/process-flashcard-generation-output-1977"
else
    echo "✅ No conflicts! Committing merge..."
    git add .
    git commit -m "Merge main with pipeline improvements"
    git push origin cursor/process-flashcard-generation-output-1977
    echo "🎉 Successfully resolved and pushed changes!"
fi
