#include <TGeoManager.h>
#include <TGeoChecker.h>
#include <TCanvas.h>
#include <iostream>

void checkGeometryOverlaps(const char* gdmlFile, bool fullCheck = false) {
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

    if (fullCheck) {
        std::cout << "Performing full geometry check..." << std::endl;
        checker.CheckGeometryFull();
        checker.PrintOverlaps();
    } else {
        std::cout << "Performing basic overlap check..." << std::endl;
        // Standard overlap checks
        gGeoManager->CheckOverlaps(tolerance,"s");
        gGeoManager->PrintOverlaps();
        
        gGeoManager->CheckOverlaps(tolerance);
        gGeoManager->PrintOverlaps();
    }

    std::cout << "Overlap checking completed." << std::endl;
    std::cout << "Check type: " << (fullCheck ? "Full" : "Basic") << std::endl;
}

void check_overlap(bool fullCheck = false) {
    // Replace "geometry.gdml" with the path to your GDML file
    const char* gdmlFile = "protodune.gdml";
    //const char* gdmlFile = "./v0/protodunevd_v4_refactored_nowires.gdml";
    checkGeometryOverlaps(gdmlFile, fullCheck);
}