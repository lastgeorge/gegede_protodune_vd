#!/usr/bin/env python
import ROOT
# ROOT.gSystem.Load('libGeom')
# geom = ROOT.TGeoManager.Import("protodune.gdml")
# geom.GetTopVolume().Draw("ogl")
# #input("Press Enter to continue...")  # keeps the window open

# # Add these lines to keep the window open
# ROOT.gApplication.Run()

# Load the necessary library
ROOT.gSystem.Load('libGeom')

# Load the GDML file
geom = ROOT.TGeoManager.Import("protodune.gdml")

# Function to display a specific volume
def display_volume(volume_name):
    volume = geom.FindVolumeFast(volume_name)
    if volume:
        volume.Draw("ogl")
    else:
        print(f"Volume '{volume_name}' not found!")

# Draw the top volume
geom.GetTopVolume().Draw("ogl")

# Print a list of all volumes for reference
print("List of volumes:")
volume_list = geom.GetListOfVolumes()
for i in range(volume_list.GetEntries()):
    print(f"{i + 1}: {volume_list.At(i).GetName()}")

# Example: Uncomment to view a specific volume
# display_volume("SpecificVolumeName")  # Replace with actual volume name

# Keep the window open for interaction
ROOT.gApplication.Run()