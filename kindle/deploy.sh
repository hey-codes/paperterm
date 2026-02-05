#!/bin/bash
#
# Deploy paperterm to Kindle
# Run this script when Kindle is mounted

KINDLE_MOUNT="/Volumes/Kindle"
EXTENSION_DIR="$KINDLE_MOUNT/extensions/paperterm"

# Check if Kindle is mounted
if [ ! -d "$KINDLE_MOUNT" ]; then
    echo "Error: Kindle not mounted at $KINDLE_MOUNT"
    echo "Please connect Kindle and enable USB transfer mode"
    exit 1
fi

# Check for extensions directory
if [ ! -d "$KINDLE_MOUNT/extensions" ]; then
    echo "Error: No extensions directory found"
    echo "Is KUAL installed?"
    exit 1
fi

echo "Deploying paperterm to Kindle..."

# Create extension directory
mkdir -p "$EXTENSION_DIR"

# Copy files
cp -v "$(dirname "$0")/TRMNL.sh" "$EXTENSION_DIR/"
cp -v "$(dirname "$0")/config.xml" "$EXTENSION_DIR/"
cp -v "$(dirname "$0")/menu.json" "$EXTENSION_DIR/"

# Make script executable
chmod +x "$EXTENSION_DIR/TRMNL.sh"

echo ""
echo "Deployment complete!"
echo ""
echo "To use:"
echo "  1. Safely eject Kindle"
echo "  2. Open KUAL"
echo "  3. Select 'paperterm' > 'Start Dashboard'"
echo ""
echo "To exit dashboard:"
echo "  Touch the bottom-right corner of the screen"
