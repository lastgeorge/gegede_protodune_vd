#include <TGeoManager.h>
#include <TGeoChecker.h>
#include <TCanvas.h>
#include <iostream>

void checkGeometryOverlaps(const char* gdmlFile) {
    // Load the GDML geometry file
    TGeoManager::Import(gdmlFile);

    if (!gGeoManager) {
        std::cerr << "Error: Unable to load GDML file: " << gdmlFile << std::endl;
        return;
    }

    // Set the top volume
    TGeoVolume* topVolume = gGeoManager->GetTopVolume();
    if (!topVolume) {
        std::cerr << "Error: No top volume found in the geometry." << std::endl;
        return;
    }

    std::cout << "Top volume: " << topVolume->GetName() << std::endl;

    // Create a TGeoChecker instance
    TGeoChecker checker(gGeoManager);

    // Perform overlap checking with a specified precision
    double tolerance = 0.001; // Tolerance for overlaps in cm
    std::cout << "Checking overlaps with a tolerance of " << tolerance << " cm..." << std::endl;

    // // Create a canvas for visualization
    // TCanvas *c1 = new TCanvas("c1", "Geometry Visualization", 800, 600);
    
    // // Draw the geometry
    // gGeoManager->GetTopVolume()->Draw("ogl");
    
    // // Set some visualization options
    // gGeoManager->SetVisLevel(4);  // Set visualization depth
    // gGeoManager->SetVisOption(0); // Set visualization option

    // Check for overlaps in the geometry - pass the top volume and tolerance
    // checker.CheckOverlaps(topVolume, tolerance,"s");

    gGeoManager->CheckOverlaps(tolerance,"s");
    gGeoManager->PrintOverlaps();

    gGeoManager->CheckOverlaps(tolerance);
    gGeoManager->PrintOverlaps();

    // You can also check recursive overlaps
    // std::cout << "\nPerforming recursive overlap check..." << std::endl;
    // topVolume->CheckOverlaps(tolerance, "s"); // 's' option for recursive check
    
    // checker.CheckGeometryFull();
    // checker.PrintOverlaps();

    // // Update the canvas
    // c1->Update();
    // c1->Draw();

    // Report completion
    std::cout << "Overlap checking completed." << std::endl;
    // std::cout << "The geometry should be visible in the ROOT canvas." << std::endl;
}

void check_overlap() {
    // Replace "geometry.gdml" with the path to your GDML file
    const char* gdmlFile = "protodune.gdml";
    //const char* gdmlFile = "./v0/protodunevd_v4_refactored_nowires.gdml";
    checkGeometryOverlaps(gdmlFile);
}