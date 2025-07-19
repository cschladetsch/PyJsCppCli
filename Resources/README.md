# Resources Directory

Resource files for AI CLI documentation, assets, and generated diagrams.

## Files

- `Arch.png` - Architecture diagram (PNG format)
- `Arch - Copy.png` - Backup copy of architecture diagram
- `Arch.svg` - Architecture diagram (SVG format)
- `Demo.gif` - Demo animation
- `Image.jpg` - Sample image

## Generated Content

This directory also serves as the output location for:
- **Doxygen diagrams**: `.dot` files converted to PNG format via CMake
- **Architecture diagrams**: Generated documentation visuals
- **Build artifacts**: Documentation-related outputs

## Build System Integration

The CMake build system automatically:
1. **Finds all `.dot` files** throughout the project
2. **Converts them to PNG** using Graphviz/dot
3. **Outputs to this directory** for easy access
4. **Updates on build** - run `./b` to regenerate

### Example Usage
```bash
./b                    # Build and generate diagrams
make docs              # Generate Doxygen documentation (if available)
make diagrams          # Convert .dot files to PNG in Resources/
```

## Description

This directory contains visual assets, documentation resources, utility scripts, and auto-generated diagrams used for AI CLI documentation and presentations. It serves as the central location for all visual documentation elements.